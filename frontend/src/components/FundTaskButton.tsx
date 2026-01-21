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
      console.error('Approve error:', approveError)
      const errorMsg = (approveError as Error)?.message || 'Unknown error'
      setError(`Approval failed: ${errorMsg.substring(0, 100)}`)
      setStep('idle')
      toast.error('Approval failed - check console')
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

    console.log('Starting approval...', {
      tokenAddress: MOCK_CNGN_ADDRESS,
      spender: FLOW_ESCROW_ADDRESS,
      amount: budgetWei.toString(),
    })

    try {
      writeApprove({
        address: MOCK_CNGN_ADDRESS,
        abi: ERC20_ABI,
        functionName: 'approve',
        args: [FLOW_ESCROW_ADDRESS, budgetWei],
      })
    } catch (err) {
      console.error('Approval call failed:', err)
      setError('Failed to initiate approval. Check console for details.')
      setStep('idle')
      toast.error('Approval failed to start')
    }
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
    <div className="space-y-3">
      <button
        onClick={handleFund}
        disabled={disabled || isLoading || !isConnected}
        className={`
          w-full px-6 py-3.5 rounded-xl font-semibold transition-all duration-300
          flex items-center justify-center gap-2.5
          disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
          ${isLoading
            ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/30'
            : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 hover:-translate-y-0.5 active:translate-y-0'
          }
        `}
      >
        {isLoading ? (
          <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
        <span>{getButtonText()}</span>
      </button>

      {error && (
        <div className="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
          <svg className="w-4 h-4 text-red-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {step !== 'idle' && (
        <div className="bg-white/80 backdrop-blur-sm rounded-xl p-3 border border-gray-200">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 flex-1">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                step === 'approving' || step === 'waiting_approval'
                  ? 'bg-amber-100 text-amber-700 ring-2 ring-amber-400 ring-offset-1'
                  : isApproveConfirmed
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-gray-100 text-gray-400'
              }`}>
                {isApproveConfirmed ? '✓' : '1'}
              </div>
              <span className={`text-xs font-medium ${step === 'approving' || step === 'waiting_approval' ? 'text-amber-700' : isApproveConfirmed ? 'text-emerald-700' : 'text-gray-400'}`}>
                Approve
              </span>
            </div>
            <div className={`w-8 h-0.5 rounded-full transition-colors ${isApproveConfirmed ? 'bg-emerald-400' : 'bg-gray-200'}`} />
            <div className="flex items-center gap-2 flex-1 justify-center">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                step === 'funding' || step === 'waiting_funding'
                  ? 'bg-amber-100 text-amber-700 ring-2 ring-amber-400 ring-offset-1'
                  : isFundConfirmed
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-gray-100 text-gray-400'
              }`}>
                {isFundConfirmed ? '✓' : '2'}
              </div>
              <span className={`text-xs font-medium ${step === 'funding' || step === 'waiting_funding' ? 'text-amber-700' : isFundConfirmed ? 'text-emerald-700' : 'text-gray-400'}`}>
                Fund
              </span>
            </div>
            <div className={`w-8 h-0.5 rounded-full transition-colors ${isFundConfirmed ? 'bg-emerald-400' : 'bg-gray-200'}`} />
            <div className="flex items-center gap-2 flex-1 justify-end">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                step === 'updating_backend'
                  ? 'bg-amber-100 text-amber-700 ring-2 ring-amber-400 ring-offset-1'
                  : 'bg-gray-100 text-gray-400'
              }`}>
                3
              </div>
              <span className={`text-xs font-medium ${step === 'updating_backend' ? 'text-amber-700' : 'text-gray-400'}`}>
                Confirm
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
