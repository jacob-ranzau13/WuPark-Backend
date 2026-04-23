FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}


RUN pip install --no-cache-dir -r requirements.txt

COPY image_processor.py ${LAMBDA_TASK_ROOT}
COPY postToItemsDb.py ${LAMBDA_TASK_ROOT}
COPY getStallInfo.py ${LAMBDA_TASK_ROOT}

CMD [ "image_processor.process_image_stream" ]
