import { useState, useEffect, useRef } from 'react';
import { useForm, UseFormProps, UseFormReturn, FieldValues, SubmitHandler, SubmitErrorHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { buildDynamicFormSchema } from '@/lib/form-validation';

/**
 * Options for the useZodForm hook
 */
export interface UseZodFormOptions<TFieldValues extends FieldValues> extends Omit<UseFormProps<TFieldValues>, 'resolver'> {
  schema?: z.ZodType<TFieldValues>;
  fields?: any[]; // Form fields to build a dynamic schema from
  onSubmit?: SubmitHandler<TFieldValues>;
  onError?: SubmitErrorHandler<TFieldValues>;
}

/**
 * Result from the useZodForm hook
 */
export interface UseZodFormResult<TFieldValues extends FieldValues> extends UseFormReturn<TFieldValues> {
  submitForm: () => void;
  isSubmitting: boolean;
  isSubmitted: boolean;
  isSubmitSuccessful: boolean;
  submitError: Error | null;
}

/**
 * Custom hook for creating a form with Zod validation
 * Can take either a Zod schema directly or build one from form fields
 */
export function useZodForm<TFieldValues extends FieldValues = FieldValues>({
  schema,
  fields,
  onSubmit,
  onError,
  ...formOptions
}: UseZodFormOptions<TFieldValues>): UseZodFormResult<TFieldValues> {
  // Internal form state for UI feedback
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitSuccessful, setIsSubmitSuccessful] = useState(false);
  const [submitError, setSubmitError] = useState<Error | null>(null);
  
  // Build schema from fields if provided and no schema is given directly
  const [resolvedSchema, setResolvedSchema] = useState<z.ZodType | undefined>(schema);
  
  // Use a ref to track if this is the first render
  const isInitialRender = useRef(true);
  
  // Use a ref to track the previous fields value
  const prevFieldsRef = useRef(fields);
  
  useEffect(() => {
    // Skip the first render or if fields haven't changed
    if (isInitialRender.current) {
      isInitialRender.current = false;
      return;
    }
    
    // Check if fields have actually changed
    const fieldsChanged = JSON.stringify(prevFieldsRef.current) !== JSON.stringify(fields);
    
    if (!schema && fields && fieldsChanged) {
      const dynamicSchema = buildDynamicFormSchema(fields);
      setResolvedSchema(dynamicSchema as any);
      prevFieldsRef.current = fields;
    } else if (schema !== resolvedSchema) {
      setResolvedSchema(schema);
    }
  }, [schema, fields, resolvedSchema]);
  
  // Setup form with Zod resolver
  const formMethods = useForm<TFieldValues>({
    ...formOptions,
    resolver: resolvedSchema ? zodResolver(resolvedSchema) : undefined,
  });
  
  // Handle form submission
  const submitForm = async () => {
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      await formMethods.handleSubmit(
        async (data) => {
          if (onSubmit) {
            await onSubmit(data);
          }
          setIsSubmitSuccessful(true);
        },
        (errors) => {
          setIsSubmitSuccessful(false);
          if (onError) {
            onError(errors);
          }
        }
      )();
    } catch (error) {
      setIsSubmitSuccessful(false);
      setSubmitError(error instanceof Error ? error : new Error(String(error)));
    } finally {
      setIsSubmitting(false);
      setIsSubmitted(true);
    }
  };
  
  return {
    ...formMethods,
    submitForm,
    isSubmitting,
    isSubmitted,
    isSubmitSuccessful,
    submitError,
  };
}

export default useZodForm; 