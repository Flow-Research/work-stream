import { useState, useEffect } from 'react'
import { useAccount, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { parseUnits } from 'viem'
import toast from 'react-hot-toast'
import { taskService } from '../services/api'

const MOCK_CNGN_ADDRESS = '0xfdf794bfBC24bCc7aE733a33a78CE16e71024821' as const
const FLOW_ESCROW_ADDRESS = '0xf10D75Bd61eA5071677aE209FD3a9aA334Ac14FF' as const

const ERC20_ABI = [
  {
    name: 'approve',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ type: 'bool' }],
  },
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ type: 'uint256' }],
  },
] as const

const ESCROW_ABI = [
  {
    name: 'fundTask',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [{ name: 'amount', type: 'uint256' }],
    outputs: [{ type: 'uint256' }],
  },
] as const

interface FundTaskButtonProps {
  taskId: string
  budgetCngn: string
  onSuccess: () => void
  disabled?: boolean
}

type FundingStep = 'idle' | 'approving' | 'waiting_approval' | 'funding' | 'waiting_funding' | 'updating_backend'

export default function FundTaskButton({
  taskId,
  budgetCngn,
  onSuccess,
  disabled = false,
}: FundTaskButtonProps) {
  const { isConnected } = useAccount()
  const [step, setStep] = useState<FundingStep>('idle')
  const [error, setError] = useState<string | null>(null)

  const budgetWei = parseUnits(budgetCngn, 18)

  const { 
    writeContract: writeApprove, 
    data: approveHash,
    isPending: isApprovePending,
    error: approveError,
  } = useWriteContract()

  const { 
    writeContract: writeFund, 
    data: fundHash,
    isPending: isFundPending,
    error: fundError,
  } = useWriteContract()

  const { 
    isLoading: isApproveConfirming, 
    isSuccess: isApproveConfirmed,
  } = useWaitForTransactionReceipt({
    hash: approveHash,
  })

  const { 
    isLoading: isFundConfirming, 
    isSuccess: isFundConfirmed,
  } = useWaitForTransactionReceipt({
    hash: fundHash,
  })

  useEffect(() => {
    if (approveError) {
      setError('Failed to approve token spending. Please try again.')
      setStep('idle')
      toast.error('Approval failed')
    }
  }, [approveError])

  useEffect(() => {
    if (fundError) {
      setError('Failed to fund task. Please try again.')
      setStep('idle')
      toast.error('Funding failed')
    }
  }, [fundError])

  useEffect(() => {
    if (isApproveConfirmed && step === 'waiting_approval') {
      setStep('funding')
      writeFund({
        address: FLOW_ESCROW_ADDRESS,
        abi: ESCROW_ABI,
        functionName: 'fundTask',
        args: [budgetWei],
      })
    }
  }, [isApproveConfirmed, step, writeFund, budgetWei])

  useEffect(() => {
    if (isFundConfirmed && fundHash && step === 'waiting_funding') {
      setStep('updating_backend')
      
      taskService.fund(taskId, fundHash)
        .then(() => {
          toast.success('Task funded successfully!')
          setStep('idle')
          onSuccess()
        })
        .catch(() => {
          setError('Task funded on chain but failed to update backend. Please contact support.')
          setStep('idle')
          toast.error('Backend update failed')
        })
    }
  }, [isFundConfirmed, fundHash, step, taskId, onSuccess])

  useEffect(() => {
    if (isApprovePending) setStep('approving')
    else if (isApproveConfirming) setStep('waiting_approval')
    else if (isFundPending) setStep('funding')
    else if (isFundConfirming) setStep('waiting_funding')
  }, [isApprovePending, isApproveConfirming, isFundPending, isFundConfirming])

  const handleFund = async () => {
    if (!isConnected) {
      toast.error('Please connect your wallet first')
      return
    }

    setError(null)
    setStep('approving')

    writeApprove({
      address: MOCK_CNGN_ADDRESS,
      abi: ERC20_ABI,
      functionName: 'approve',
      args: [FLOW_ESCROW_ADDRESS, budgetWei],
    })
  }

  const isLoading = step !== 'idle'

  const getButtonText = () => {
    switch (step) {
      case 'approving':
        return 'Approving...'
      case 'waiting_approval':
        return 'Confirming Approval...'
      case 'funding':
        return 'Funding...'
      case 'waiting_funding':
        return 'Confirming Funding...'
      case 'updating_backend':
        return 'Updating...'
      default:
        return `Fund Task (₦${parseFloat(budgetCngn).toLocaleString()})`
    }
  }

  return (
    <div className="space-y-2">
      <button
        onClick={handleFund}
        disabled={disabled || isLoading || !isConnected}
        className="w-full px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isLoading && (
          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {getButtonText()}
      </button>
      
      {error && (
        <p className="text-sm text-red-600 text-center">{error}</p>
      )}
      
      {step !== 'idle' && (
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${step === 'approving' || step === 'waiting_approval' ? 'bg-amber-400 animate-pulse' : isApproveConfirmed ? 'bg-green-400' : 'bg-gray-300'}`} />
            <span>Approve</span>
          </div>
          <span className="text-gray-300">→</span>
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${step === 'funding' || step === 'waiting_funding' ? 'bg-amber-400 animate-pulse' : isFundConfirmed ? 'bg-green-400' : 'bg-gray-300'}`} />
            <span>Fund</span>
          </div>
          <span className="text-gray-300">→</span>
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${step === 'updating_backend' ? 'bg-amber-400 animate-pulse' : 'bg-gray-300'}`} />
            <span>Confirm</span>
          </div>
        </div>
      )}
    </div>
  )
}
