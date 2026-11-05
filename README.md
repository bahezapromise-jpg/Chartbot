igali Pizza Assistant: Streamlit demo 
The Week 9 hybrid chatbot as a web page. Three files go together in one public GitHub 
repository: app.py, requirements.txt and intent_classifier.joblib. 
1. Create a public repository and upload the three files. 
2. Go to share.streamlit.io and sign in with GitHub. 
3. Create app, then choose the repository, the branch main and the main file app.py. 
4. Deploy. The first start installs the libraries and the spaCy model: a few minutes. 
The classifier was trained with scikit-learn 1.8.0; requirements.txt pins that version so it loads 
the same way. Never put a bot token or an API key in the repository: Streamlit has its own 
Secrets box (app settings). 
