const core = require('@actions/core');
const github = require('@actions/github');

try {
    // `website_url`, `verbose` inputs defined in action metadata file
    const websiteUrl = core.getInput('website_url');
    const verboseMode = core.getInput('verbose');
    console.log(`Verbose mode: ${verboseMode}`);
    console.log(`Checking website: ${websiteUrl}!`);
    const time = (new Date()).toTimeString();
    core.setOutput("time", time);

    if(verboseMode.toLowerCase() === 'true') {
        // Get the JSON webhook payload for the event that triggered the workflow
        const payload = JSON.stringify(github.context.payload, undefined, 2)
        console.log(`The event payload: ${payload}`);
    }
  } catch (error) {
    core.setFailed(error.message);
  }