# &nbsp; ![YOCCO](https://raw.githubusercontent.com/juliakreutzer/yocco/master/static/img/logo.png)

Submission the [Climate Change AI Hackathon 2019, Montreal.](https://climate-change-ai-hackathon.devpost.com/)

## Webapp

Built with Flask. Following [this tutorial](https://github.com/avinassh/pytorch-flask-api-heroku/blob/master/README.md).

Run the server:

	FLASK_ENV=development FLASK_APP=app.py python3.5 -m flask run

And upload pictures to try out the garbage detection AI. Example test images are in `test_images`.

## Mobile App
HTMLs in khaled/YOCCO

## Image Recognition
Our image recognition models are based on pre-trained models (DenseNet121 and MobileNet, trained on ImageNet) provided by [Torch](https://pytorch.org/docs/stable/torchvision/models.html) and [Keras](https://keras.io/applications/#mobilenet). We fine-tuned MobileNet to classify garbage material based on the [TrashNet data collection](https://github.com/garythung/trashnet).

## Contributors
Julia Kreutzer, Salma Elmahallawy, Khaled Matloub, Kene Nnodu, Reza Filsoof

