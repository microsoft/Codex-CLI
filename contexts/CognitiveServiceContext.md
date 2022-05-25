# Cognitive Service Powershell context

## Using Speech Synthesis

This project includes speech synthesized playback for your query outputs using the azure cognitive services speech cli. As noted in the previous section about contexts, this is a certain behaviour of the model that is included in the sample `powershell-voice-cognitive-service.txt` file available in the `contexts` folder. Before running any speech synthesis output from the model, you have to do a couple of steps to set it up: 

### Set up Azure Speech Service

Speech Service is part of the larger Cognitive Services suite and helps you enable applications in areas of speech-to-text, text-to-speech, and speech translation. Here we want it primarily for the text-to-speech functionality. 

1. Go to the Cognitive Services Hub in the Azure Portal 

2. Create a new Speech Service: You may choose the default values for setting it up

3. Save the API Key and Region for further use

### Set up Azure Speech CLI 

Follow the instructions in [Azure Speech CLI Quickstart](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/spx-basics?tabs=windowsinstall%2Cterminal) to install the prerequisites

If you are setting up for the first time, here is what you may have to do: 
1. Download [.NET Core 3.1 SDK](https://docs.microsoft.com/en-us/dotnet/core/install/windows) and [Microsoft Visual C++ Redistributable for Visual Studio 2019](https://support.microsoft.com/help/2977003/the-latest-supported-visual-c-downloads)
2. Install speech CLI in PowerShell using this command: `dotnet tool install --global Microsoft.CognitiveServices.Speech.CLI`
3. Use the subsription key and region that you obtained from the Cognitive Services Speech Service page and input into the following commands

For Terminal:  
`spx config @key --set SUBSCRIPTION-KEY`  
`spx config @region --set REGION`

For Powershell:  
`spx --% config @key --set SUBSCRIPTION-KEY`  
`spx --% config @region --set REGION`  

### Load the example speech context file

Load the example Cognitive Services speech context file using  ` # load context powershell-voice-cognitive-service.txt ` and then hit Ctrl + G to let the Codex CLI load the file

And that's it! To get started with an example, go ahead and type `# whats the meaning of life`.
You can develop your own context with more speech functions as mentioned in the previous section. 