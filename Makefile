.PHONY: run build logs

CTFD := ./test/CTFd
PROJ := ./src/*

clean:
	rm -rf $(CTFD)/CTFD/plugins/kube_ctf && mkdir -p $(CTFD)/CTFD/plugins/kube_ctf

build:
	$(MAKE) clean && cp -r $(PROJ) $(CTFD)/CTFd/plugins/kube_ctf && cd $(CTFD) && docker-compose build

run:
	$(MAKE) build && cd $(CTFD) && docker-compose up -d

logs:
	cd $(CTFD) && docker-compose logs -f

stop:
	cd $(CTFD) && docker-compose stop

stop-force:
	cd $(CTFD) && docker-compose stop -t 0