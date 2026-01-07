// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title FlowEscrow
 * @notice Escrow contract for Flow research task payments
 * @dev Handles deposit, release, and dispute resolution for task payments
 */
contract FlowEscrow is AccessControl, ReentrancyGuard {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    IERC20 public cNGN;

    enum TaskStatus {
        Funded,      // Client deposited funds
        InProgress,  // Work has started
        Completed,   // All subtasks approved, funds released
        Disputed,    // Dispute raised, funds frozen
        Cancelled,   // Cancelled before work started
        Resolved     // Dispute resolved
    }

    struct Task {
        uint256 id;
        address client;
        uint256 totalAmount;
        uint256 releasedAmount;
        TaskStatus status;
        uint256 createdAt;
    }

    struct SubtaskPayment {
        address worker;
        uint256 amount;
        bool paid;
    }

    uint256 public taskCounter;
    uint256 public platformFeeBps = 1000; // 10% = 1000 basis points
    address public feeRecipient;

    mapping(uint256 => Task) public tasks;
    mapping(uint256 => mapping(uint256 => SubtaskPayment)) public subtaskPayments;
    // taskId => subtaskIndex => payment

    event TaskFunded(uint256 indexed taskId, address indexed client, uint256 amount);
    event SubtaskApproved(uint256 indexed taskId, uint256 subtaskIndex, address worker, uint256 amount);
    event TaskCompleted(uint256 indexed taskId);
    event TaskDisputed(uint256 indexed taskId, address disputedBy);
    event DisputeResolved(uint256 indexed taskId, address winner);
    event TaskCancelled(uint256 indexed taskId, uint256 refundAmount);
    event FeeUpdated(uint256 oldFee, uint256 newFee);
    event FeeRecipientUpdated(address oldRecipient, address newRecipient);

    error InvalidAmount();
    error TaskNotFound();
    error InvalidTaskStatus();
    error NotAuthorized();
    error ExceedsBudget();
    error AlreadyPaid();
    error TransferFailed();
    error FeeTooHigh();
    error InvalidAddress();
    error WorkAlreadyStarted();

    constructor(address _cNGN, address _feeRecipient) {
        if (_cNGN == address(0) || _feeRecipient == address(0)) revert InvalidAddress();
        
        cNGN = IERC20(_cNGN);
        feeRecipient = _feeRecipient;
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @notice Client deposits funds to create escrow for a task
     * @param amount Amount of cNGN to deposit
     * @return taskId The ID of the created task
     */
    function fundTask(uint256 amount) external nonReentrant returns (uint256) {
        if (amount == 0) revert InvalidAmount();
        if (!cNGN.transferFrom(msg.sender, address(this), amount)) revert TransferFailed();

        unchecked {
            taskCounter++;
        }
        
        tasks[taskCounter] = Task({
            id: taskCounter,
            client: msg.sender,
            totalAmount: amount,
            releasedAmount: 0,
            status: TaskStatus.Funded,
            createdAt: block.timestamp
        });

        emit TaskFunded(taskCounter, msg.sender, amount);
        return taskCounter;
    }

    /**
     * @notice Release payment for approved subtask (requires client + admin confirmation)
     * @param taskId The task ID
     * @param subtaskIndex The subtask index
     * @param worker The worker address to pay
     * @param amount The payment amount
     */
    function approveSubtask(
        uint256 taskId,
        uint256 subtaskIndex,
        address worker,
        uint256 amount
    ) external nonReentrant {
        Task storage task = tasks[taskId];
        if (task.id == 0) revert TaskNotFound();
        if (task.status != TaskStatus.Funded && task.status != TaskStatus.InProgress) {
            revert InvalidTaskStatus();
        }
        if (msg.sender != task.client && !hasRole(ADMIN_ROLE, msg.sender)) {
            revert NotAuthorized();
        }
        if (task.releasedAmount + amount > task.totalAmount) revert ExceedsBudget();

        SubtaskPayment storage payment = subtaskPayments[taskId][subtaskIndex];
        if (payment.paid) revert AlreadyPaid();

        // Calculate fees
        uint256 fee = (amount * platformFeeBps) / 10000;
        uint256 workerAmount = amount - fee;

        // Update state before transfers
        payment.worker = worker;
        payment.amount = amount;
        payment.paid = true;
        task.releasedAmount += amount;
        task.status = TaskStatus.InProgress;

        // Transfer funds
        if (!cNGN.transfer(worker, workerAmount)) revert TransferFailed();
        if (!cNGN.transfer(feeRecipient, fee)) revert TransferFailed();

        emit SubtaskApproved(taskId, subtaskIndex, worker, workerAmount);
    }

    /**
     * @notice Mark task as complete (after all subtasks approved)
     * @param taskId The task ID
     */
    function completeTask(uint256 taskId) external nonReentrant {
        Task storage task = tasks[taskId];
        if (task.id == 0) revert TaskNotFound();
        if (msg.sender != task.client && !hasRole(ADMIN_ROLE, msg.sender)) {
            revert NotAuthorized();
        }
        if (task.status != TaskStatus.InProgress) revert InvalidTaskStatus();

        task.status = TaskStatus.Completed;

        // Refund any unused budget
        uint256 remaining = task.totalAmount - task.releasedAmount;
        if (remaining > 0) {
            if (!cNGN.transfer(task.client, remaining)) revert TransferFailed();
        }

        emit TaskCompleted(taskId);
    }

    /**
     * @notice Raise a dispute (freezes remaining funds)
     * @param taskId The task ID
     */
    function raiseDispute(uint256 taskId) external {
        Task storage task = tasks[taskId];
        if (task.id == 0) revert TaskNotFound();
        if (task.status != TaskStatus.Funded && task.status != TaskStatus.InProgress) {
            revert InvalidTaskStatus();
        }
        // Anyone involved can raise dispute (validated off-chain)

        task.status = TaskStatus.Disputed;
        emit TaskDisputed(taskId, msg.sender);
    }

    /**
     * @notice Admin resolves dispute
     * @param taskId The task ID
     * @param winner The winner's address
     * @param winnerAmount Amount to pay the winner
     */
    function resolveDispute(
        uint256 taskId,
        address winner,
        uint256 winnerAmount
    ) external onlyRole(ADMIN_ROLE) nonReentrant {
        Task storage task = tasks[taskId];
        if (task.status != TaskStatus.Disputed) revert InvalidTaskStatus();

        uint256 remaining = task.totalAmount - task.releasedAmount;
        if (winnerAmount > remaining) revert ExceedsBudget();

        task.status = TaskStatus.Resolved;
        task.releasedAmount += winnerAmount;

        if (winnerAmount > 0) {
            if (!cNGN.transfer(winner, winnerAmount)) revert TransferFailed();
        }

        // Refund rest to client
        uint256 refund = remaining - winnerAmount;
        if (refund > 0) {
            if (!cNGN.transfer(task.client, refund)) revert TransferFailed();
        }

        emit DisputeResolved(taskId, winner);
    }

    /**
     * @notice Cancel task before work starts
     * @param taskId The task ID
     */
    function cancelTask(uint256 taskId) external nonReentrant {
        Task storage task = tasks[taskId];
        if (task.id == 0) revert TaskNotFound();
        if (msg.sender != task.client && !hasRole(ADMIN_ROLE, msg.sender)) {
            revert NotAuthorized();
        }
        if (task.status != TaskStatus.Funded) revert WorkAlreadyStarted();
        if (task.releasedAmount > 0) revert WorkAlreadyStarted();

        task.status = TaskStatus.Cancelled;
        if (!cNGN.transfer(task.client, task.totalAmount)) revert TransferFailed();

        emit TaskCancelled(taskId, task.totalAmount);
    }

    /**
     * @notice Update platform fee (admin only)
     * @param newFeeBps New fee in basis points
     */
    function setFee(uint256 newFeeBps) external onlyRole(ADMIN_ROLE) {
        if (newFeeBps > 2000) revert FeeTooHigh(); // Max 20%
        uint256 oldFee = platformFeeBps;
        platformFeeBps = newFeeBps;
        emit FeeUpdated(oldFee, newFeeBps);
    }

    /**
     * @notice Update fee recipient
     * @param newRecipient New recipient address
     */
    function setFeeRecipient(address newRecipient) external onlyRole(ADMIN_ROLE) {
        if (newRecipient == address(0)) revert InvalidAddress();
        address oldRecipient = feeRecipient;
        feeRecipient = newRecipient;
        emit FeeRecipientUpdated(oldRecipient, newRecipient);
    }

    /**
     * @notice Get task details
     * @param taskId The task ID
     * @return Task struct
     */
    function getTask(uint256 taskId) external view returns (Task memory) {
        return tasks[taskId];
    }

    /**
     * @notice Get subtask payment details
     * @param taskId The task ID
     * @param subtaskIndex The subtask index
     * @return SubtaskPayment struct
     */
    function getSubtaskPayment(uint256 taskId, uint256 subtaskIndex) 
        external 
        view 
        returns (SubtaskPayment memory) 
    {
        return subtaskPayments[taskId][subtaskIndex];
    }
}
