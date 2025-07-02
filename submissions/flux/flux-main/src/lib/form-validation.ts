/**
 * Form validation utilities
 * 
 * This file provides utilities for form validation using Zod,
 * including common patterns and schemas
 */
import { z } from 'zod';

/**
 * Common validation patterns
 */
export const PATTERNS = {
  // Match email addresses (basic validation)
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  
  // Match phone numbers (10-15 digits, optional + prefix)
  PHONE: /^\+?[0-9]{10,15}$/,
  
  // Match URLs
  URL: /^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+([\/\w-]*)*(\?[^\s]*)?$/,
  
  // Match strong passwords (min 8 chars, at least 1 uppercase, 1 lowercase, 1 number)
  STRONG_PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/,
}

/**
 * Common error messages
 */
export const ERROR_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_PHONE: 'Please enter a valid phone number',
  INVALID_URL: 'Please enter a valid URL',
  MIN_LENGTH: (min: number) => `Must be at least ${min} characters`,
  MAX_LENGTH: (max: number) => `Must be at most ${max} characters`,
  PASSWORD_WEAK: 'Password must have at least 8 characters with numbers and letters',
  FILE_TOO_LARGE: (maxMB: number) => `File size exceeds the maximum limit of ${maxMB}MB`,
  INVALID_FILE_TYPE: 'Invalid file type',
}

/**
 * Form field validation schemas
 */
export const fieldValidators = {
  // Text field with required validation and optional min/max length
  text: (options?: { required?: boolean, minLength?: number, maxLength?: number }) => {
    let schema = z.string();
    
    if (options?.minLength) {
      schema = schema.min(options.minLength, ERROR_MESSAGES.MIN_LENGTH(options.minLength));
    }
    
    if (options?.maxLength) {
      schema = schema.max(options.maxLength, ERROR_MESSAGES.MAX_LENGTH(options.maxLength));
    }
    
    return options?.required 
      ? schema.min(1, ERROR_MESSAGES.REQUIRED)
      : schema.optional();
  },
  
  // Email field with validation
  email: (required = false) => {
    const schema = z.string().regex(PATTERNS.EMAIL, ERROR_MESSAGES.INVALID_EMAIL);
    return required ? schema.min(1, ERROR_MESSAGES.REQUIRED) : schema.optional();
  },
  
  // Phone field with validation
  phone: (required = false) => {
    const schema = z.string().regex(PATTERNS.PHONE, ERROR_MESSAGES.INVALID_PHONE);
    return required ? schema.min(1, ERROR_MESSAGES.REQUIRED) : schema.optional();
  },
  
  // URL field with validation
  url: (required = false) => {
    const schema = z.string().regex(PATTERNS.URL, ERROR_MESSAGES.INVALID_URL);
    return required ? schema.min(1, ERROR_MESSAGES.REQUIRED) : schema.optional();
  },
  
  // Number field with optional min/max validation
  number: (options?: { required?: boolean, min?: number, max?: number }) => {
    let schema = z.coerce.number();
    
    if (options?.min !== undefined) {
      schema = schema.min(options.min);
    }
    
    if (options?.max !== undefined) {
      schema = schema.max(options.max);
    }
    
    return options?.required ? schema : schema.optional();
  },
  
  // Checkbox validation
  checkbox: (required = false) => {
    return required ? z.boolean().refine(val => val === true, ERROR_MESSAGES.REQUIRED) : z.boolean();
  },
  
  // Select/dropdown validation
  select: (options?: { required?: boolean, values?: string[] }) => {
    // If we have predefined values, use an enum schema
    if (options?.values && options.values.length > 0) {
      // Need at least one value for enum 
      const validValues = options.values.length > 0 
        ? options.values 
        : ['default_value'];
      
      const enumSchema = z.enum([validValues[0], ...validValues.slice(1)] as [string, ...string[]]);
      return options?.required ? enumSchema : enumSchema.optional();
    }
    
    // Otherwise use a string schema
    const schema = z.string();
    return options?.required 
      ? schema.min(1, ERROR_MESSAGES.REQUIRED) 
      : schema.optional();
  },
  
  // Multi-select validation
  multiSelect: (options?: { required?: boolean, values?: string[], minItems?: number, maxItems?: number }) => {
    let schema = z.array(z.string());
    
    if (options?.required || options?.minItems) {
      const min = options?.minItems || 1;
      schema = schema.min(min);
    }
    
    if (options?.maxItems) {
      schema = schema.max(options.maxItems);
    }
    
    // Add validation for allowed values if specified
    if (options?.values && options.values.length > 0) {
      return schema.refine(
        items => items.every(item => options.values!.includes(item)),
        "One or more selected values are invalid"
      );
    }
    
    return schema;
  },
};

/**
 * Helper to build dynamic form validation schema from form fields
 */
export function buildDynamicFormSchema(fields: any[]) {
  if (!Array.isArray(fields) || fields.length === 0) {
    return z.object({}).optional();
  }
  
  const schemaMap: Record<string, z.ZodTypeAny> = {};
  
  fields.forEach(field => {
    if (!field.id || !field.type) return;

    // Skip heading fields (h1, h2, h3) as they don't need validation
    if (['h1', 'h2', 'h3'].includes(field.type)) return;
    
    // Skip AI fields as they are computed automatically and don't need user validation
    if (field.type === 'ai' || field.is_ai_field) return;
    
    switch (field.type) {
      case 'text':
      case 'shortText':
        schemaMap[field.id] = fieldValidators.text({ 
          required: field.required,
          minLength: field.validation?.min,
          maxLength: field.validation?.max,
        });
        break;
        
      case 'long_answer':
      case 'longText':
        schemaMap[field.id] = fieldValidators.text({ 
          required: field.required,
          minLength: field.validation?.min,
          maxLength: field.validation?.max,
        });
        break;
        
      case 'email':
        schemaMap[field.id] = fieldValidators.email(field.required);
        break;
        
      case 'phone':
        schemaMap[field.id] = fieldValidators.phone(field.required);
        break;
        
      case 'number':
        schemaMap[field.id] = fieldValidators.number({
          required: field.required,
          min: field.validation?.min,
          max: field.validation?.max,
        });
        break;
        
      case 'checkbox':
        schemaMap[field.id] = fieldValidators.checkbox(field.required);
        break;
        
      case 'multiple_choice':
      case 'radio':
      case 'dropdown':
      case 'select':
        schemaMap[field.id] = fieldValidators.select({
          required: field.required,
          values: field.options,
        });
        break;
        
      case 'multi_select':
      case 'multiSelect':
        schemaMap[field.id] = fieldValidators.multiSelect({
          required: field.required,
          values: field.options,
          minItems: field.required ? 1 : undefined,
        });
        break;
        
      case 'link':
      case 'url':
        schemaMap[field.id] = fieldValidators.url(field.required);
        break;
        
      // Add more field types as needed
        
      default:
        // Default to basic string validation for unknown types
        schemaMap[field.id] = field.required 
          ? z.string().min(1, ERROR_MESSAGES.REQUIRED) 
          : z.string().optional();
    }
  });
  
  return z.object(schemaMap);
} 