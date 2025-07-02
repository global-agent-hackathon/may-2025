import { z } from 'zod';

// Schema for form field options
export const fieldOptionsSchema = z.object({
  min: z.number().optional(),
  max: z.number().optional(),
  pattern: z.string().optional(),
  fileSize: z.number().optional(),
  fileTypes: z.array(z.string()).optional(),
});

// Schema for form fields
export const formFieldSchema = z.object({
  id: z.string(),
  type: z.enum([
    'shortText',
    'longText',
    'number',
    'email',
    'phone',
    'date',
    'select',
    'multiSelect',
    'checkbox',
    'radio',
    'fileUpload',
    'url',
    'h1',
    'h2',
    'h3',
    'ai'
  ]),
  label: z.string().min(1, 'Label is required'),
  placeholder: z.string().optional(),
  required: z.boolean().default(false),
  options: z.array(z.string()).optional(),
  description: z.string().optional(),
  validation: fieldOptionsSchema.optional(),
  // AI field properties
  is_ai_field: z.boolean().optional(),
  ai_metadata_prompt: z.string().optional(),
  ai_computed_value: z.string().optional(),
});

// Schema for a form - modified to make fields optional for settings page
export const formSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  fields: z.array(formFieldSchema).default([]),
  published: z.boolean().default(false),
  workspaceId: z.string().optional(),
  banner: z.string().optional(),
});

// Schema for form creation
export const formCreateSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  workspaceId: z.string().optional(),
});

// Schema for form response
export const formResponseSchema = z.record(z.string(), z.any());

// TypeScript types derived from the Zod schemas
export type FormField = z.infer<typeof formFieldSchema>;
export type Form = z.infer<typeof formSchema>;
export type FormCreate = z.infer<typeof formCreateSchema>;
export type FormResponse = z.infer<typeof formResponseSchema>; 