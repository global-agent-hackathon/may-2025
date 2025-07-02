import { create } from 'zustand'
import { v4 as uuidv4 } from 'uuid'

export type FieldType = 
  | 'shortText'
  | 'longText'
  | 'number'
  | 'email'
  | 'phone'
  | 'date'
  | 'select'
  | 'multiSelect'
  | 'checkbox'
  | 'radio'
  | 'fileUpload'
  | 'url'
  | 'ai'

export interface FormField {
  id: string
  type: FieldType
  label: string
  placeholder?: string
  required: boolean
  options?: string[] // For select, multiSelect, radio
  description?: string
  validation?: {
    min?: number
    max?: number
    pattern?: string
  }
}

interface FormState {
  fields: FormField[]
  title: string
  description: string
  addField: (field: Omit<FormField, 'id'>) => void
  updateField: (id: string, field: Partial<FormField>) => void
  removeField: (id: string) => void
  updateFormMeta: (meta: { title?: string; description?: string }) => void
  reorderFields: (startIndex: number, endIndex: number) => void
}

export const useFormStore = create<FormState>((set) => ({
  fields: [],
  title: 'Untitled Form',
  description: '',
  
  addField: (field) => 
    set((state) => ({
      fields: [...state.fields, { ...field, id: uuidv4() }]
    })),
    
  updateField: (id, field) =>
    set((state) => ({
      fields: state.fields.map((f) => 
        f.id === id ? { ...f, ...field } : f
      )
    })),
    
  removeField: (id) =>
    set((state) => ({
      fields: state.fields.filter((f) => f.id !== id)
    })),
    
  updateFormMeta: (meta) =>
    set((state) => ({
      ...state,
      ...meta
    })),
    
  reorderFields: (startIndex, endIndex) =>
    set((state) => {
      const newFields = [...state.fields]
      const [removed] = newFields.splice(startIndex, 1)
      newFields.splice(endIndex, 0, removed)
      return { fields: newFields }
    })
})) 