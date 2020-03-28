var editor = null;

const getTextSelection = function (editor) {
  const selection = window.getSelection();

  if (selection != null && selection.rangeCount > 0) {
    const range = selection.getRangeAt(0);

    return {
      start: getTextLength(editor, range.startContainer, range.startOffset),
      end: getTextLength(editor, range.endContainer, range.endOffset)
    };
  } else
    return null;
}

const getTextLength = function (parent, node, offset) {
  var textLength = 0;

  if (node.nodeName == '#text')
    textLength += offset;
  else for (var i = 0; i < offset; i++)
    if (node) {
      textLength += getNodeTextLength(node.childNodes[i]);
    }

  if (node && node != parent && node.parentNode)
    textLength += getTextLength(parent, node.parentNode, getNodeOffset(node));

  return textLength;
}

const getNodeTextLength = function (node) {
  var textLength = 0;

  if (node.nodeName == 'BR')
    textLength = 1;
  else if (node.nodeName == '#text')
    textLength = node.nodeValue.length;
  else if (node.childNodes != null)
    for (var i = 0; i < node.childNodes.length; i++)
      textLength += getNodeTextLength(node.childNodes[i]);

  return textLength;
}

const getNodeOffset = function (node) {
  return node == null ? -1 : 1 + getNodeOffset(node.previousSibling);
}

const handleSelectionChange = function () {
  if (isEditor(document.activeElement)) {
    const textSelection = getTextSelection(document.activeElement);

    if (textSelection != null) {
      const text = document.activeElement.innerText;
      const selection = text.slice(textSelection.start, textSelection.end);
    }
    console.log(text);
  }
}

const isEditor = function (element) {
  return element != null && element.classList.contains('post-body');
}


