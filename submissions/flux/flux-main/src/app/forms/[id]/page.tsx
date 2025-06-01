"use client"

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Check, Loader2, Save } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { InteractiveHoverButton } from '@/components/magicui/interactive-hover-button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { prepareFieldsForUI } from '@/lib/form-helpers'
import { useZodForm } from '@/hooks/use-zod-form'
import { toast } from 'sonner'

interface FormData {
  id: string
  title: string
  description?: string
  published: boolean
  banner?: string
  fields: FormField[]
}

interface FormField {
  id: string
  type: string
  label: string
  required: boolean
  placeholder?: string
  options?: string[]
  fileTypes?: string[]
  fileSize?: number
  validation?: {
    min?: number
    max?: number
  }
  // AI field properties
  is_ai_field?: boolean
  ai_metadata_prompt?: string
  ai_computed_value?: string
}

export default function PublicFormPage() {
  const params = useParams()
  const router = useRouter()
  const formId = params.id as string
  
  const [form, setForm] = useState<FormData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [bannerImage, setBannerImage] = useState<string | null>(null)
  
  // Setup form with Zod validation
  const { 
    register, 
    control, 
    formState: { errors }, 
    setValue,
    watch,
    submitForm,
    isSubmitting,
    submitError 
  } = useZodForm({
    fields: form?.fields || [],
    onSubmit: async (data) => {
      if (!form) return;
      
      try {
        // Convert file objects to base64 if present
        const formData: Record<string, any> = { ...data };
        
        // Process file uploads
        const filePromises: Promise<any>[] = [];
        form.fields.forEach(field => {
          if (field.type === 'file' && data[field.id] && data[field.id] instanceof File) {
            filePromises.push(
              fileToBase64(data[field.id]).then(base64 => {
                // Extract only the base64 content without the data URL prefix
                const base64Content = base64.split(',')[1];
                
                formData[field.id] = {
                  fileName: data[field.id].name,
                  fileType: data[field.id].type,
                  fileSize: data[field.id].size,
                  content: base64Content,
                  // Add mime type and extension for easier handling
                  mimeType: data[field.id].type,
                  extension: data[field.id].name.split('.').pop()?.toLowerCase() || ''
                };
              })
            );
          }
        });
        
        if (filePromises.length > 0) {
          await Promise.all(filePromises);
        }
        
        // Compute AI field values
        const aiFields = form.fields.filter(field => field.is_ai_field && field.ai_metadata_prompt);
        for (const aiField of aiFields) {
          try {
            const response = await fetch('/api/compute-ai-field', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                ai_field_id: aiField.id,
                ai_metadata_prompt: aiField.ai_metadata_prompt,
                form_data: {
                  form_fields: form.fields,
                  field_data: formData
                }
              }),
            });
            
            if (response.ok) {
              const result = await response.json();
              formData[aiField.id] = result.computed_value;
            } else {
              console.error(`Failed to compute AI field ${aiField.id}:`, await response.text());
              // Set a default value if AI computation fails
              formData[aiField.id] = 'AI computation failed';
            }
          } catch (error) {
            console.error(`Error computing AI field ${aiField.id}:`, error);
            formData[aiField.id] = 'AI computation error';
          }
        }
        
        console.log(`Submitting form to: /api/forms/${formId}/responses`);
        
        // Submit the form data
        const response = await fetch(`/api/forms/${formId}/responses`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });
        
        // Get the full response text to diagnose any issues
        const responseText = await response.text();
        console.log(`Response status: ${response.status}, Response text:`, responseText);
        
        // Parse the response if possible
        let responseData;
        try {
          responseData = JSON.parse(responseText);
        } catch (e) {
          console.error('Failed to parse response as JSON:', e);
        }
        
        if (!response.ok) {
          console.error('Form submission error:', responseData || responseText);
          throw new Error(responseData?.error || 'Failed to submit form');
        }
        
        setIsSubmitted(true);
        toast.success('Form submitted successfully');
      } catch (error) {
        console.error('Error submitting form:', error);
        toast.error('Failed to submit form. Please try again.');
        throw error; // Let the form hook handle the error
      }
    },
    onError: (errors) => {
      console.error('Validation errors:', errors);
      toast.error('Please fix the errors in the form');
    }
  });
  
  // Watch form values for file uploads
  const formValues = watch();
  
  useEffect(() => {
    const fetchForm = async () => {
      try {
        const response = await fetch(`/api/forms/${formId}?public=true`)
        if (!response.ok) {
          throw new Error('Form not found or not published')
        }
        
        const formData = await response.json()
        
        if (!formData.published) {
          throw new Error('This form is not currently accepting responses')
        }
        
        // Log banner data for debugging
        console.log('Form data received:', { 
          banner: formData.banner,
          hasFields: Array.isArray(formData.fields),
          fieldCount: Array.isArray(formData.fields) ? formData.fields.length : 0
        });
        
        // Ensure field types are compatible with the UI
        if (formData.fields && Array.isArray(formData.fields)) {
          formData.fields = prepareFieldsForUI(formData.fields);
        }
        
        setForm(formData)
        
        // Setup form validation
        const validationRules: Record<string, any> = {};
        
        // Initialize form values for fields that need it
        formData.fields.forEach((field: FormField) => {
          if (field.type === 'checkbox') {
            if (field.options && field.options.length > 0) {
              setValue(field.id, []);
              if (field.required) {
                validationRules[field.id] = {
                  validate: (value: string[]) => (Array.isArray(value) && value.length > 0) || 'Please select at least one option'
                };
              }
            } else {
              setValue(field.id, false);
              if (field.required) {
                validationRules[field.id] = {
                  validate: (value: boolean) => value === true || 'This checkbox is required'
                };
              }
            }
          } else if (field.type === 'multiple_choice' || field.type === 'dropdown') {
            setValue(field.id, '');
            if (field.required) {
              validationRules[field.id] = {
                validate: (value: string) => !!value || 'Please select an option'
              };
            }
          } else if (field.type === 'multi_select') {
            setValue(field.id, []);
            if (field.required) {
              validationRules[field.id] = {
                validate: (value: string[]) => (Array.isArray(value) && value.length > 0) || 'Please select at least one option'
              };
            }
          }
        });
        
        // Register custom validation rules
        Object.entries(validationRules).forEach(([fieldId, rules]) => {
          if (rules) {
            register(fieldId, rules);
          }
        });
        
        // Set banner if available and not empty
        if (formData.banner) {
          console.log('Setting banner image:', formData.banner.substring(0, 50) + '...');
          setBannerImage(formData.banner);
        } else {
          console.log('No banner found in form data');
          setBannerImage(null);
        }
      } catch (error) {
        console.error('Error fetching form:', error)
        toast.error('Error loading form. Please try again later.');
      } finally {
        setIsLoading(false)
      }
    }
    
    if (formId) {
      fetchForm()
    }
    
    // Cleanup function
    return () => {
      // No cleanup needed
    };
  }, [formId, setValue, register])
  
  // Handle file input change
  const handleFileChange = (fieldId: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setValue(fieldId, file);
    }
  };
  
  // Function to convert file to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  };
  
  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6 py-8">
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
          <p className="text-muted-foreground">Loading form...</p>
        </div>
      ) : !form ? (
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold mb-4">Form not found</h1>
          <p className="text-muted-foreground mb-6">This form may not exist or is no longer accepting responses.</p>
          <Button onClick={() => router.push('/')}>Go to Homepage</Button>
        </div>
      ) : isSubmitted ? (
        <div className="text-center py-12 space-y-4">
          <div className="bg-green-50 text-green-700 rounded-full w-16 h-16 mx-auto flex items-center justify-center mb-4">
            <Check className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold">Form submitted successfully!</h1>
          <p className="text-muted-foreground">Thank you for your response.</p>
          <Button 
            onClick={() => router.push('/')}
            className="mt-4"
          >
            Go to Homepage
          </Button>
        </div>
      ) : (
        <>
          {/* Display banner if available */}
          {bannerImage && (
            <div className="mb-6">
              <img src={bannerImage} alt="Form banner" className="w-full h-48 object-cover rounded-lg" />
            </div>
          )}
          
          <div className="space-y-4">
            <h1 className="text-3xl font-bold">{form.title}</h1>
            {form.description && (
              <p className="text-muted-foreground">{form.description}</p>
            )}
          </div>
          
          <form onSubmit={(e) => { e.preventDefault(); submitForm(); }} className="space-y-8">
            {form.fields
              .filter(field => !field.is_ai_field) // Hide AI fields from users
              .map((field) => (
              <div 
                key={field.id} 
                className="bg-white rounded-lg shadow-sm p-6"
              >
                {/* Heading fields */}
                {field.type === 'h1' && (
                  <h1 className="text-2xl font-bold">{field.label}</h1>
                )}
                
                {field.type === 'h2' && (
                  <h2 className="text-xl font-bold">{field.label}</h2>
                )}
                
                {field.type === 'h3' && (
                  <h3 className="text-lg font-bold">{field.label}</h3>
                )}
                
                {/* Regular input fields with labels */}
                {field.type !== 'h1' && field.type !== 'h2' && field.type !== 'h3' && (
                  <div className="space-y-3">
                    <Label 
                      htmlFor={field.id} 
                      className="text-base font-medium block"
                    >
                      {field.label} 
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </Label>
                    
                    {field.type === 'text' && (
                      <Input
                        id={field.id}
                        placeholder={field.placeholder || ""}
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          required: field.required ? 'This field is required' : false,
                          minLength: field.validation?.min ? {
                            value: field.validation.min,
                            message: `Must be at least ${field.validation.min} characters`
                          } : undefined,
                          maxLength: field.validation?.max ? {
                            value: field.validation.max,
                            message: `Cannot exceed ${field.validation.max} characters`
                          } : undefined
                        })}
                      />
                    )}
                    
                    {field.type === 'long_answer' && (
                      <Textarea
                        id={field.id}
                        placeholder={field.placeholder || ""}
                        className={`min-h-[100px] ${errors[field.id] ? 'border-red-500' : ''}`}
                        {...register(field.id, {
                          required: field.required ? 'This field is required' : false,
                          minLength: field.validation?.min ? {
                            value: field.validation.min,
                            message: `Must be at least ${field.validation.min} characters`
                          } : undefined,
                          maxLength: field.validation?.max ? {
                            value: field.validation.max,
                            message: `Cannot exceed ${field.validation.max} characters`
                          } : undefined
                        })}
                      />
                    )}
                    
                    {field.type === 'number' && (
                      <Input
                        id={field.id}
                        type="number"
                        placeholder={field.placeholder || ""}
                        min={field.validation?.min}
                        max={field.validation?.max}
                        step="any"
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          valueAsNumber: true,
                          validate: value => {
                            if (field.required && (value === undefined || value === null || isNaN(value))) {
                              return 'This field is required';
                            }
                            if (field.validation?.min !== undefined && value < field.validation.min) {
                              return `Value must be at least ${field.validation.min}`;
                            }
                            if (field.validation?.max !== undefined && value > field.validation.max) {
                              return `Value cannot exceed ${field.validation.max}`;
                            }
                            return true;
                          }
                        })}
                      />
                    )}
                    
                    {field.type === 'email' && (
                      <Input
                        id={field.id}
                        type="email"
                        placeholder={field.placeholder || "name@example.com"}
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          required: field.required ? 'Email is required' : false,
                          pattern: {
                            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                            message: 'Please enter a valid email address'
                          }
                        })}
                      />
                    )}
                    
                    {field.type === 'phone' && (
                      <Input
                        id={field.id}
                        type="tel"
                        placeholder={field.placeholder || "+1 (555) 000-0000"}
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          required: field.required ? 'Phone number is required' : false,
                          pattern: {
                            value: /^\+?[0-9]{10,15}$/,
                            message: 'Please enter a valid phone number'
                          }
                        })}
                      />
                    )}
                    
                    {field.type === 'date' && (
                      <Input
                        id={field.id}
                        type="date"
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          required: field.required ? 'Date is required' : false,
                          valueAsDate: true
                        })}
                      />
                    )}
                    
                    {field.type === 'time' && (
                      <Input
                        id={field.id}
                        type="time"
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          required: field.required ? 'Time is required' : false
                        })}
                      />
                    )}
                    
                    {(field.type === 'link' || field.type === 'url') && (
                      <Input
                        id={field.id}
                        type="url"
                        placeholder={field.placeholder || "https://example.com"}
                        className={errors[field.id] ? 'border-red-500' : ''}
                        {...register(field.id, {
                          required: field.required ? 'URL is required' : false,
                          pattern: {
                            value: /^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+([\/\w-]*)*(\?[^\s]*)?$/,
                            message: 'Please enter a valid URL'
                          }
                        })}
                      />
                    )}
                    
                    {field.type === 'checkbox' && field.options && field.options.length > 0 ? (
                      <div className="space-y-2">
                        {field.options.map((option, i) => (
                          <div key={i} className="flex items-center space-x-2">
                            <Checkbox
                              id={`${field.id}-${i}`}
                              checked={Array.isArray(formValues[field.id]) && formValues[field.id].includes(option)}
                              onCheckedChange={(checked) => {
                                const currentValues = Array.isArray(formValues[field.id]) ? [...formValues[field.id]] : [];
                                if (checked) {
                                  setValue(field.id, [...currentValues, option], { shouldValidate: field.required });
                                } else {
                                  setValue(field.id, currentValues.filter(val => val !== option), { shouldValidate: field.required });
                                }
                              }}
                            />
                            <Label htmlFor={`${field.id}-${i}`} className="font-normal">
                              {option}
                            </Label>
                          </div>
                        ))}
                        {field.required && errors[field.id] && (
                          <p className="text-sm text-red-500 mt-1">
                            Please select at least one option
                          </p>
                        )}
                      </div>
                    ) : field.type === 'checkbox' ? (
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id={field.id}
                          checked={formValues[field.id] || false}
                          onCheckedChange={(checked) => {
                            setValue(field.id, checked === true, {
                              shouldValidate: field.required
                            });
                          }}
                        />
                        <Label htmlFor={field.id} className="font-normal">
                          {field.placeholder || "Yes"}
                        </Label>
                      </div>
                    ) : null}
                    
                    {field.type === 'multiple_choice' && field.options && field.options.length > 0 && (
                      <RadioGroup
                        value={formValues[field.id] || ''}
                        onValueChange={(value) => {
                          setValue(field.id, value, {
                            shouldValidate: field.required
                          });
                        }}
                        className="space-y-2"
                      >
                        {field.options.map((option, i) => (
                          <div key={i} className="flex items-center space-x-2">
                            <RadioGroupItem value={option} id={`${field.id}-${i}`} />
                            <Label htmlFor={`${field.id}-${i}`} className="font-normal">
                              {option}
                            </Label>
                          </div>
                        ))}
                        {field.required && !formValues[field.id] && errors[field.id] && (
                          <p className="text-sm text-red-500 mt-1">
                            Please select an option
                          </p>
                        )}
                      </RadioGroup>
                    )}
                    
                    {field.type === 'dropdown' && field.options && field.options.length > 0 && (
                      <Select
                        value={formValues[field.id] || ''}
                        onValueChange={(value) => {
                          setValue(field.id, value, {
                            shouldValidate: field.required
                          });
                        }}
                      >
                        <SelectTrigger className={errors[field.id] ? 'border-red-500' : ''}>
                          <SelectValue placeholder={field.placeholder || "Select an option"} />
                        </SelectTrigger>
                        <SelectContent>
                          {field.options.map((option, i) => (
                            <SelectItem key={i} value={option}>
                              {option}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                    
                    {field.type === 'multi_select' && field.options && field.options.length > 0 && (
                      <div className="space-y-2">
                        {field.options.map((option, i) => (
                          <div key={i} className="flex items-center space-x-2">
                            <Checkbox 
                              id={`${field.id}-${i}`} 
                              checked={Array.isArray(formValues[field.id]) && formValues[field.id].includes(option)}
                              onCheckedChange={(checked) => {
                                const currentValues = Array.isArray(formValues[field.id]) ? [...formValues[field.id]] : [];
                                if (checked) {
                                  setValue(field.id, [...currentValues, option], {
                                    shouldValidate: field.required
                                  });
                                } else {
                                  setValue(field.id, currentValues.filter(val => val !== option), {
                                    shouldValidate: field.required
                                  });
                                }
                              }}
                            />
                            <Label htmlFor={`${field.id}-${i}`} className="font-normal">
                              {option}
                            </Label>
                          </div>
                        ))}
                        {field.required && errors[field.id] && (
                          <p className="text-sm text-red-500 mt-1">
                            Please select at least one option
                          </p>
                        )}
                      </div>
                    )}
                    
                    {field.type === 'file' && (
                      <div>
                        <Input
                          id={field.id}
                          type="file"
                          className={errors[field.id] ? 'border-red-500' : ''}
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              // Check file size if specified
                              const maxSize = field.fileSize ? field.fileSize * 1024 * 1024 : 5 * 1024 * 1024; // Default 5MB
                              if (file.size > maxSize) {
                                toast.error(`File size exceeds the maximum limit of ${field.fileSize || 5}MB`);
                                e.target.value = ''; // Clear input
                                return;
                              }
                              
                              // Check file type if specified
                              if (field.fileTypes && field.fileTypes.length > 0) {
                                const isValidType = field.fileTypes.some(type => 
                                  file.type === type || file.name.endsWith(`.${type.split('/')[1]}`)
                                );
                                if (!isValidType) {
                                  toast.error(`Invalid file type. Allowed: ${field.fileTypes.join(', ')}`);
                                  e.target.value = ''; // Clear input
                                  return;
                                }
                              }
                              
                              setValue(field.id, file);
                            } else if (field.required) {
                              setValue(field.id, undefined);
                            }
                          }}
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          {field.fileTypes?.join(', ') || "All file types"} allowed. 
                          Max size: {field.fileSize || 5}MB
                        </p>
                      </div>
                    )}
                    
                    {/* Display validation error */}
                    {errors[field.id] && (
                      <p className="text-sm text-red-500 mt-1">
                        {errors[field.id]?.message?.toString() || 'This field is required'}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
            
            <div className="mt-8 flex items-start justify-start pb-10">
              <InteractiveHoverButton
                type="submit"
                disabled={isSubmitting}
                className="w-start flex items-start justify-start border-black bg-black px-6 py-2 text-sm text-white hover:bg-gray-800 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <Loader2 className="h-4 w-5 animate-spin" />
                    Submitting...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Save className="h-4 w-5" />
                    Submit
                  </span>
                )}
              </InteractiveHoverButton>
            </div>
            
            {/* Display form-level error */}
            {submitError && (
              <div className="mt-4 p-3 bg-red-50 text-red-800 rounded-md">
                <p>An error occurred: {submitError.message}</p>
                <p className="text-sm">Please try again or contact support if the problem persists.</p>
              </div>
            )}
          </form>
        </>
      )}
    </div>
  )
}