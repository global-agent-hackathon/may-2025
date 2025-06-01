export function convertMarkdownToHtml(markdown) {
    // Convert simple markdown to HTML
    const html = markdown
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')  // H3
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')   // H2
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')    // H1
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>') // Bold
        .replace(/\*(.*)\*/gim, '<em>$1</em>')     // Italics
        .replace(/\[([^\]]+)\]\((.*?)\)/gim, '<a href="$2">$1</a>'); // Links

    return html;
}
