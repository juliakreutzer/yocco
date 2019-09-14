# yocco

## Webapp

Built with Flask.

Run the server:

	FLASK_ENV=development FLASK_APP=app.py python3.5 -m flask run

Upload an image for classification from the command line:
	
	curl -X POST -F "file=@./app/test_images/dog.jpg" http://localhost:5000/predict

The output should be `{"class_name": "Labrador_retriever"}`.
