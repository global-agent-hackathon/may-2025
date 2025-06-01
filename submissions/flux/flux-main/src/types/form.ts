import { Form } from '@prisma/client';

export interface FormItem extends Form {
  title: string;
  description: string | null;
  schema: any; // JSON schema for form fields
  published: boolean;
  userId: string;
  workspaceId: string | null;
  isDeleted: boolean;
  deletedAt: Date | null;
  isInTrash: boolean;
  createdAt: Date;
  updatedAt: Date;
} 