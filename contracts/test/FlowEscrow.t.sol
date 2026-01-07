// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/FlowEscrow.sol";
import "../src/MockCNGN.sol";

contract FlowEscrowTest is Test {
    FlowEscrow public escrow;
    MockCNGN public cngn;
    
    address public admin = address(1);
    address public client = address(2);
    address public worker = address(3);
    address public feeRecipient = address(4);
    
    uint256 public constant TASK_BUDGET = 100000; // 1000 cNGN
    uint256 public constant SUBTASK_PAYMENT = 20000; // 200 cNGN

    function setUp() public {
        vm.startPrank(admin);
        
        // Deploy mock token
        cngn = new MockCNGN();
        
        // Deploy escrow
        escrow = new FlowEscrow(address(cngn), feeRecipient);
        
        vm.stopPrank();
        
        // Fund client
        vm.prank(client);
        cngn.faucet();
        
        // Approve escrow to spend client's tokens
        vm.prank(client);
        cngn.approve(address(escrow), type(uint256).max);
    }

    function test_FundTask() public {
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        assertEq(taskId, 1);
        
        FlowEscrow.Task memory task = escrow.getTask(taskId);
        assertEq(task.client, client);
        assertEq(task.totalAmount, TASK_BUDGET);
        assertEq(task.releasedAmount, 0);
        assertEq(uint256(task.status), uint256(FlowEscrow.TaskStatus.Funded));
    }

    function test_FundTask_RevertOnZeroAmount() public {
        vm.prank(client);
        vm.expectRevert(FlowEscrow.InvalidAmount.selector);
        escrow.fundTask(0);
    }

    function test_ApproveSubtask() public {
        // Fund task
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        // Approve subtask
        vm.prank(client);
        escrow.approveSubtask(taskId, 0, worker, SUBTASK_PAYMENT);
        
        // Check payment was made (minus fee)
        uint256 fee = (SUBTASK_PAYMENT * 1000) / 10000; // 10%
        uint256 workerAmount = SUBTASK_PAYMENT - fee;
        
        assertEq(cngn.balanceOf(worker), workerAmount);
        assertEq(cngn.balanceOf(feeRecipient), fee);
        
        // Check task state
        FlowEscrow.Task memory task = escrow.getTask(taskId);
        assertEq(task.releasedAmount, SUBTASK_PAYMENT);
        assertEq(uint256(task.status), uint256(FlowEscrow.TaskStatus.InProgress));
    }

    function test_ApproveSubtask_RevertOnExceedBudget() public {
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        vm.prank(client);
        vm.expectRevert(FlowEscrow.ExceedsBudget.selector);
        escrow.approveSubtask(taskId, 0, worker, TASK_BUDGET + 1);
    }

    function test_ApproveSubtask_RevertOnUnauthorized() public {
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        vm.prank(worker);
        vm.expectRevert(FlowEscrow.NotAuthorized.selector);
        escrow.approveSubtask(taskId, 0, worker, SUBTASK_PAYMENT);
    }

    function test_CompleteTask() public {
        // Fund task
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        // Approve some subtasks
        vm.prank(client);
        escrow.approveSubtask(taskId, 0, worker, SUBTASK_PAYMENT);
        
        // Complete task
        vm.prank(client);
        escrow.completeTask(taskId);
        
        FlowEscrow.Task memory task = escrow.getTask(taskId);
        assertEq(uint256(task.status), uint256(FlowEscrow.TaskStatus.Completed));
        
        // Check client received refund
        uint256 expectedRefund = TASK_BUDGET - SUBTASK_PAYMENT;
        assertGt(cngn.balanceOf(client), 0);
    }

    function test_CancelTask() public {
        uint256 clientBalanceBefore = cngn.balanceOf(client);
        
        // Fund task
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        // Cancel task
        vm.prank(client);
        escrow.cancelTask(taskId);
        
        FlowEscrow.Task memory task = escrow.getTask(taskId);
        assertEq(uint256(task.status), uint256(FlowEscrow.TaskStatus.Cancelled));
        
        // Check client received full refund
        assertEq(cngn.balanceOf(client), clientBalanceBefore);
    }

    function test_CancelTask_RevertAfterWorkStarted() public {
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        vm.prank(client);
        escrow.approveSubtask(taskId, 0, worker, SUBTASK_PAYMENT);
        
        vm.prank(client);
        vm.expectRevert(FlowEscrow.WorkAlreadyStarted.selector);
        escrow.cancelTask(taskId);
    }

    function test_RaiseDispute() public {
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        vm.prank(client);
        escrow.raiseDispute(taskId);
        
        FlowEscrow.Task memory task = escrow.getTask(taskId);
        assertEq(uint256(task.status), uint256(FlowEscrow.TaskStatus.Disputed));
    }

    function test_ResolveDispute() public {
        vm.prank(client);
        uint256 taskId = escrow.fundTask(TASK_BUDGET);
        
        vm.prank(client);
        escrow.raiseDispute(taskId);
        
        // Admin resolves dispute in favor of worker
        uint256 winnerAmount = TASK_BUDGET / 2;
        vm.prank(admin);
        escrow.resolveDispute(taskId, worker, winnerAmount);
        
        FlowEscrow.Task memory task = escrow.getTask(taskId);
        assertEq(uint256(task.status), uint256(FlowEscrow.TaskStatus.Resolved));
        assertEq(cngn.balanceOf(worker), winnerAmount);
    }

    function test_SetFee() public {
        vm.prank(admin);
        escrow.setFee(500); // 5%
        
        assertEq(escrow.platformFeeBps(), 500);
    }

    function test_SetFee_RevertOnTooHigh() public {
        vm.prank(admin);
        vm.expectRevert(FlowEscrow.FeeTooHigh.selector);
        escrow.setFee(2001); // > 20%
    }

    function test_SetFeeRecipient() public {
        address newRecipient = address(5);
        
        vm.prank(admin);
        escrow.setFeeRecipient(newRecipient);
        
        assertEq(escrow.feeRecipient(), newRecipient);
    }
}
