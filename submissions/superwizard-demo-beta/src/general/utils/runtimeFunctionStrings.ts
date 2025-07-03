// TypeScript function
function scrollIntoViewFunction() {
  // @ts-expect-error this is run in the browser context
  this.scrollIntoView({
    block: 'center',
    inline: 'center',
    behavior: 'auto',
  });
}
// Convert the TypeScript function to a string
export const scrollScriptString = scrollIntoViewFunction.toString();
