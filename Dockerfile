FROM python:3.10-slim

WORKDIR /opt
ADD . /opt/ayd
RUN cd ayd && \
    pip install . && \
    cp -r docs .. && \
    cd .. && \
    rm -rf ayd && \
    rm -rf ~/.cache

RUN python -m nltk.downloader "punkt"
ENV AYD_DEBUG_MODE False
EXPOSE 8000
CMD ["uvicorn", "askyourdocs.app:app", "--host", "0.0.0.0", "--port", "8000"]
