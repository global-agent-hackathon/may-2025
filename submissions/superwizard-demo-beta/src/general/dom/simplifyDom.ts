// console.log('Content script loaded..');

import { callRPC } from '../browser/pageRPC';
// Remove the import from the enhanced directory
// import { EnhancedDOMProcessor } from './enhanced';
import { truthyFilter } from '../../general/utils/utils';

// Essential attributes and tags configuration
const CONFIG = {
  attributes: {
    essential: ['data-id', 'role', 'aria-label'],
    interactive: ['data-interactive', 'data-visible', 'data-clickable']
  },
  tags: {
    interactive: [
      'button', 'a', 'input', 'select', 'textarea', 'form', 'label',
      'option', 'fieldset', 'nav', 'header', 'footer', 'main', 'section'
    ],
    heavy: [
      'svg', 'img', 'canvas', 'video', 'source', 'picture', 'iframe',
      'path', 'rect', 'circle', 'polygon'
    ],
    skip: ['script', 'style', 'link', 'meta', 'noscript']  // Removed 'path' as it might contain viewBox data
  }
};

// Core LayerElement interface
export interface LayerElement {
  id: string;
  tagName: string;
  attributes: Record<string, string>;
  textContent?: string;  // Added to preserve text content
  children: (LayerElement | null)[];
}

/**
 * Gets a simplified DOM representation
 */
export async function getSimplifiedDom() {
  const fullDom = await callRPC('getAnnotatedDOM', [], 3);
  if (!fullDom) return "No page content available";

  const dom = new DOMParser().parseFromString(fullDom, 'text/html');
  applyDOMProcessing(dom.documentElement);
  const baseLayer = processFlattenedLayer(dom.documentElement);
  return getOptimizedDomHtml(baseLayer);
}

/**
 * Enhances aria-label with context information
 */
function enhanceAriaLabel(element: Element): string {
  const tagName = element.tagName.toLowerCase();
  const type = element.getAttribute('type');
  let label = element.getAttribute('aria-label') || element.textContent?.trim() || '';
  
  if (label.length > 100) {
    label = label.substring(0, 100) + '...';
  }

  if (label) {
    if (CONFIG.tags.interactive.includes(tagName) && !label.includes(tagName)) {
      label = `${tagName}: ${label}`;
    }
    if (tagName === 'input' && type && !label.includes(type)) {
      label += ` (${type})`;
    }
  } else {
    label = tagName + (type ? ` (${type})` : '');
  }

  return label;
}

/**
 * Gets direct text content of an element, excluding child elements
 */
function getDirectTextContent(element: Element): string {
  let text = '';
  for (const node of element.childNodes) {
    if (node.nodeType === Node.TEXT_NODE) {
      text += node.textContent?.trim() || '';
    }
  }
  return text;
}

/**
 * Apply attribute filtering and processing to the DOM tree
 */
function applyDOMProcessing(element: Element) {
  if (element.nodeType !== Node.ELEMENT_NODE) return;

  const htmlElement = element as HTMLElement;
  const tagName = element.tagName.toLowerCase();
  const isInteractive = CONFIG.tags.interactive.includes(tagName) ||
                       element.hasAttribute('role') ||
                       element.hasAttribute('aria-label');

  if (isInteractive || element.hasAttribute('data-id')) {
    const enhancedLabel = enhanceAriaLabel(element);
    if (isInteractive && enhancedLabel) {
      const parentLabel = element.parentElement?.getAttribute('aria-label') || '';
      if (!parentLabel.includes(enhancedLabel)) {
        htmlElement.setAttribute('aria-label', enhancedLabel);
      }
    }
  }

  // Keep only essential attributes
  Array.from(htmlElement.attributes)
    .forEach(attr => {
      if (!CONFIG.attributes.essential.includes(attr.name.toLowerCase())) {
        htmlElement.removeAttribute(attr.name);
      }
    });

  Array.from(element.children).forEach(applyDOMProcessing);
}

/**
 * Process DOM into a flattened layer representation
 */
function processFlattenedLayer(element: Element): LayerElement | null {
  const tagName = element.tagName.toLowerCase();
  
  if (CONFIG.tags.skip.includes(tagName)) return null;

  const attributes: Record<string, string> = {};
  Array.from(element.attributes).forEach(attr => {
    if (CONFIG.attributes.essential.includes(attr.name.toLowerCase())) {
      attributes[attr.name] = attr.value;
    }
  });

  // Get direct text content
  const directText = getDirectTextContent(element);

  const hasOnlyDataId = Object.keys(attributes).length === 1 && 'data-id' in attributes;
  const hasRoleOrAriaLabel = 'role' in attributes || 'aria-label' in attributes;
  const hasImportantAttributes = hasRoleOrAriaLabel || (!hasOnlyDataId && Object.keys(attributes).length > 0);
  const isInteractiveTag = CONFIG.tags.interactive.includes(tagName);
  const hasText = directText.length > 0;

  if (CONFIG.tags.heavy.includes(tagName)) {
    return (hasImportantAttributes || hasText) ? {
      id: element.id || Math.random().toString(36).substr(2, 9),
      tagName,
      attributes,
      textContent: directText || undefined,
      children: []
    } : null;
  }

  const processedChildren = Array.from(element.children)
    .map(child => processFlattenedLayer(child))
    .filter(truthyFilter);

  // Keep element if it has text, is interactive, or has important attributes
  if (hasText || isInteractiveTag || hasImportantAttributes) {
    return {
      id: element.id || Math.random().toString(36).substr(2, 9),
      tagName,
      attributes,
      textContent: directText || undefined,
      children: processedChildren
    };
  }

  if (processedChildren.length > 0) {
    return processedChildren.length === 1 ? processedChildren[0] : {
      id: Math.random().toString(36).substr(2, 9),
      tagName: 'div',
      attributes: {},
      textContent: directText || undefined,
      children: processedChildren
    };
  }

  // Keep elements with text even if they have no other significant properties
  return hasText ? {
    id: Math.random().toString(36).substr(2, 9),
    tagName,
    attributes: {},
    textContent: directText,
    children: []
  } : null;
}

/**
 * Create optimized DOM HTML with minimal structure
 */
function getOptimizedDomHtml(baseLayer: LayerElement | null): string {
  if (!baseLayer) return '';
  
  const attrs = Object.entries(baseLayer.attributes)
    .filter(([_, value]) => value)
    .map(([key, value]) => `${key}="${value}"`)
    .join(' ');

  const textContent = baseLayer.textContent || '';
  
  const childrenHtml = baseLayer.children
    .filter(truthyFilter)
    .map(child => getOptimizedDomHtml(child))
    .join('');

  return `<div ${attrs}>${textContent}${childrenHtml}`;
}

/**
 * Removes specific attributes from an element (unused in optimized version)
 */
function removeSpecificAttributes(node: Element, attributesToRemove: string[]) {
  attributesToRemove.forEach(attr => {
    if (node.hasAttribute(attr)) {
      node.removeAttribute(attr);
    }
  });
  
  Array.from(node.children).forEach(child => 
    removeSpecificAttributes(child, attributesToRemove)
  );
}
