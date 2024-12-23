function extractProjectLabelFromNode(labelNode) {
  const labelText = labelNode.textContent.trim()
  let resultText
  if (labelText.startsWith('Choose ')) {
    resultText = labelText.substring(7)
  } else {
    resultText = labelText
  }
  return resultText
}

function buttonSelected(event) {
  const radioButton = event.target

  const label = document.querySelector(`label[for="${radioButton.id}"]`)
  const voteSubmit = document.getElementById('vote-submit')

  if (radioButton.value === 'Skip') {
    const currentProject = document.querySelector(
      `label[for="vote-current-radio"]`
    )
    if (currentProject) {
      const currentProjectLabel = extractProjectLabelFromNode(currentProject)
      voteSubmit.value = `Skip ${currentProjectLabel}`
    } else {
      voteSubmit.value = 'Confirm Skip'
    }
  
  } else if (label) {
    const resultText = extractProjectLabelFromNode(label)
    voteSubmit.value = `Vote for ${resultText}`
  }
  voteSubmit.disabled = false
}

;(function () {
  document.getElementsByName('action').forEach((elem) => {
    if (elem.type === 'radio') {
      elem.checked = false
      elem.onchange = buttonSelected
    }
  })

  document.getElementById('vote-submit').disabled = true
})()

