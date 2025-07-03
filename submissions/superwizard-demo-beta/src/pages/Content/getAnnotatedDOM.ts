import { NODE_ID_SELECTOR } from '../../constants';

// Track elements for later reference
let currentElements: HTMLElement[] = [];

/**
 * Processes DOM tree and adds data-id attributes
 */
function traverseDOM(node: Node, pageElements: HTMLElement[]) {
  const clonedNode = node.cloneNode(false) as Node;

  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = node as HTMLElement;
    const clonedElement = clonedNode as HTMLElement;

    // Track element and assign ID
    pageElements.push(element);
    clonedElement.setAttribute('data-id', (pageElements.length - 1).toString());
  }

  // Process children recursively
  node.childNodes.forEach((child) => {
    const result = traverseDOM(child, pageElements);
    clonedNode.appendChild(result.clonedDOM);
  });

  return {
    pageElements,
    clonedDOM: clonedNode,
  };
}

/**
 * Returns a cloned DOM with data-id attributes added to each element
 */
export default function getAnnotatedDOM() {
  currentElements = [];
  const result = traverseDOM(document.documentElement, currentElements);
  return (result.clonedDOM as HTMLElement).outerHTML;
}

/**
 * Gets or creates a unique ID for an element by its numeric index
 */
export function getUniqueElementSelectorId(id: number): string {
  const element = currentElements[id];
  let uniqueId = element.getAttribute(NODE_ID_SELECTOR);
  if (uniqueId) return uniqueId;
  
  uniqueId = Math.random().toString(36).substring(2, 10);
  element.setAttribute(NODE_ID_SELECTOR, uniqueId);
  return uniqueId;
}
