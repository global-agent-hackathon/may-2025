import * as React from "react"

import { 
  ToastActionElement, 
  ToastProps 
} from "@/components/ui/toast"

const TOAST_LIMIT = 5
const TOAST_REMOVE_DELAY = 1000

export type ToasterToast = ToastProps & {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: ToastActionElement
}

type ActionType = {
  ADD_TOAST: "ADD_TOAST",
  UPDATE_TOAST: "UPDATE_TOAST",
  DISMISS_TOAST: "DISMISS_TOAST",
  REMOVE_TOAST: "REMOVE_TOAST"
}

let count = 0

function genId() {
  count = (count + 1) % Number.MAX_VALUE
  return count.toString()
}

type Action =
  | {
      type: "ADD_TOAST"
      toast: ToasterToast
    }
  | {
      type: "UPDATE_TOAST"
      toast: Partial<ToasterToast>
    }
  | {
      type: "DISMISS_TOAST"
      toastId?: ToasterToast["id"]
    }
  | {
      type: "REMOVE_TOAST"
      toastId?: ToasterToast["id"]
    }

interface State {
  toasts: ToasterToast[]
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>()

let dispatch: React.Dispatch<Action>;

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "ADD_TOAST":
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      }

    case "UPDATE_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      }

    case "DISMISS_TOAST": {
      const { toastId } = action

      // ! Side effects ! - This could be extracted into a dismissToast() action,
      // but I'll keep it here for simplicity
      if (toastId) {
        addToRemoveQueue(toastId)
      } else {
        state.toasts.forEach((toast) => {
          addToRemoveQueue(toast.id)
        })
      }

      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === toastId || toastId === undefined
            ? {
                ...t,
                open: false,
              }
            : t
        ),
      }
    }
    case "REMOVE_TOAST":
      if (action.toastId === undefined) {
        return {
          ...state,
          toasts: [],
        }
      }
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      }
  }
}

function addToRemoveQueue(toastId: string) {
  if (toastTimeouts.has(toastId)) {
    return
  }

  const timeout = setTimeout(() => {
    toastTimeouts.delete(toastId)
    dispatch({
      type: "REMOVE_TOAST",
      toastId: toastId,
    })
  }, TOAST_REMOVE_DELAY)

  toastTimeouts.set(toastId, timeout)
}

interface ToasterContextState extends State {
  toast: (props: Omit<ToasterToast, "id">) => string
  dismiss: (toastId?: string) => void
  update: (props: ToasterToast) => void
}

const ToasterContext = React.createContext<ToasterContextState | undefined>(
  undefined
)

export const useToaster = () => {
  const context = React.useContext(ToasterContext)
  if (context === undefined) {
    throw new Error("useToaster must be used within a ToasterProvider")
  }
  return context
}

export const toast = ({
  title,
  description,
  ...props
}: Omit<ToasterToast, "id">) => {
  const id = genId()

  dispatch({
    type: "ADD_TOAST",
    toast: {
      id,
      title,
      description,
      ...props,
      open: true,
    },
  })

  return id
}

export function ToasterProvider({
  children,
}: {
  children: React.ReactNode
}): React.ReactElement {
  const [state, innerDispatch] = React.useReducer(reducer, {
    toasts: [],
  })

  // This is a hack to make the state and dispatch available to the toast function
  React.useEffect(() => {
    dispatch = innerDispatch
  }, [state])

  return (
    <ToasterContext.Provider
      value={{
        ...state,
        toast,
        dismiss: (toastId?: string) => {
          dispatch({
            type: "DISMISS_TOAST",
            toastId,
          })
        },
        update: (toast: ToasterToast) => {
          dispatch({
            type: "UPDATE_TOAST",
            toast,
          })
        },
      }}
    >
      {children}
    </ToasterContext.Provider>
  )
} 