/**
 * Helper functions for managing form field types and compatibility
 * between UI components and the API schema
 */

// Map UI field types to schema field types
export const mapUIFieldTypeToSchema = (type: string): string => {
  switch (type) {
    case 'text': return 'shortText';
    case 'long_answer': return 'longText';
    case 'number': return 'number';
    case 'email': return 'email';
    case 'phone': return 'phone';
    case 'date': return 'date';
    case 'dropdown': return 'select';
    case 'multi_select': return 'multiSelect';
    case 'checkbox': return 'checkbox';
    case 'multiple_choice': return 'radio';
    case 'file': return 'fileUpload';
    case 'h1': return 'h1';
    case 'h2': return 'h2';
    case 'h3': return 'h3';
    case 'ai': return 'ai';
    case 'time': return 'date'; // Map time to date as a fallback
    case 'link': return 'url'; // Map link to url
    default: return 'shortText'; // Default fallback
  }
}

// Map schema field types to UI field types
export const mapSchemaFieldTypeToUI = (type: string): string => {
  switch (type) {
    case 'shortText': return 'text';
    case 'longText': return 'long_answer';
    case 'number': return 'number';
    case 'email': return 'email';
    case 'phone': return 'phone';
    case 'date': return 'date';
    case 'select': return 'dropdown';
    case 'multiSelect': return 'multi_select';
    case 'checkbox': return 'checkbox';
    case 'radio': return 'multiple_choice';
    case 'fileUpload': return 'file';
    case 'url': return 'link';
    case 'h1': return 'h1';
    case 'h2': return 'h2';
    case 'h3': return 'h3';
    case 'ai': return 'ai';
    default: return 'text'; // Default fallback
  }
}

// Valid schema field types
const SCHEMA_FIELD_TYPES = [
  'shortText', 'longText', 'number', 'email', 'phone',
  'date', 'select', 'multiSelect', 'checkbox', 'radio',
  'fileUpload', 'url', 'h1', 'h2', 'h3', 'ai'
];

// Valid UI field types
const UI_FIELD_TYPES = [
  'text', 'long_answer', 'number', 'email', 'phone',
  'date', 'dropdown', 'multi_select', 'checkbox', 'multiple_choice',
  'file', 'h1', 'h2', 'h3', 'time', 'link', 'ai'
];

// Convert fields for API submission
export const prepareFieldsForAPI = (fields: any[]) => {
  if (!Array.isArray(fields)) return [];
  
  return fields.map(field => {
    // Create a copy of the field
    const newField = { ...field };
    
    // Only convert if the field type is a UI type and not already a schema type
    if (field.type && UI_FIELD_TYPES.includes(field.type) && !SCHEMA_FIELD_TYPES.includes(field.type)) {
      newField.type = mapUIFieldTypeToSchema(field.type);
    }
    
    return newField;
  });
}

// Convert fields for UI display
export const prepareFieldsForUI = (fields: any[]) => {
  if (!Array.isArray(fields)) return [];
  
  return fields.map(field => {
    // Create a copy of the field
    const newField = { ...field };
    
    // Only convert if the field type is a schema type and not already a UI type
    if (field.type && SCHEMA_FIELD_TYPES.includes(field.type) && !UI_FIELD_TYPES.includes(field.type)) {
      newField.type = mapSchemaFieldTypeToUI(field.type);
    }
    
    return newField;
  });
} 