(function() {
  const extensionId = chrome.runtime.id;
  // Create a script element to inject the extension ID into the webpage
  const script = document.createElement('script');
  script.textContent = `window.extensionId = '${extensionId}';`;
  (document.head || document.documentElement).appendChild(script);
  script.remove();
})();