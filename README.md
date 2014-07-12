===============
KeywordAnalyzer
===============


Dependencies
============
mysql-client libmysqlclient-dev
libpq-dev


Environment
===========
$ pip install flask-wtf==0.8.4
$ pip install setuptools==0.8
$ python setup.py


Project dir structure
=====================
./app/           - app package
    sengines/
    seomoz/
    static/      - static files like images, js, style sheets
    lib/         - libraries (python)
    templates/   - Jinja2 templates
    tests/       - basic tests (nosetests)
    translations/- language mutations
./build/
./db_repository/
./tmp/
./babel.cfg
./db_create.py
./profile.py
./requirements.txt
./run.py
./tests.py


TODO
====
- jenkins - make dev env and run the project
- jenkins - install job - in virtualenv
- refactorize the code + add comments
- create interface for yahoo module
- Configuration - check if exists in database - __ini__.py ?
- moznost zobrazeni 5, 10, 50, 100 searches na stranku, nyni je 5
    - hodit do settings tabu
    - configuracna tabulka - vytvorit config form + submit button - neskor cez AJAX, nastavit
- moznost serazeni searches dle hlavicky, alespon Title, Language, DA
- inkrementovanie google queries
- radit aj podla stavu ?? - running/queued/stopped/completed
    - nova tabulka stavov!
- SearchError: Failed getting URL: timed out
    - mozno skusit viackrat stiahnut, pripadne zvysit timeout
- error logging do jedneho mailu, jednoho app.error.log stringu!
- refactoring - views.py, index.html
- implementovat vyber search enginu
- aktualnost parametrov stranok nastavit aspon na 3 dni
    - viac uloh pre rovnake klucove slovo zrejme nefunguju spravne
    - spravne pripocitavanie found ?
    - spravne vypisovanie vysledkov ?
- osetrit format CSV suborov - vynechat prazdne riadky etc.
- pagination
- mysql databaza
- sorting v tabulkach - nie je prilis narocne??
- format formulara pre nove ulohy
- do New URLs task pridat priority - este nieco ine?
- niekedy vyhodi takuto SeomozException:
    our authentication failed. Check your authentication details and try again. For more information on signed authentication, see: http://apiwiki.moz.com/signed-authentication
- JS - confirm dialogy
- dvojnasobny pocet searches pre bulk searches ? - dafuq, niekde nenulujem searches_done
- log tab - vypisovat poslednych x riadkov z app.log suboru? - najma vynimky
- no task to process vypisovat? - staci snad vypisat len raz
- Amazon Elastic Compute Cloud (Amazon EC2)
- skontrolovat vsetko v opere, chrome..aj exploreri
- vyznam filtrov ???
- lokalizacia (Flask-Babel + ikonky na frontende)
- dalsie vyhladavace (Yahoo, Bing)
- prechod na MySQL !
- skript, ktory nastavi kompletne cele prostredie
- seomoz vynimky (viac nez 1 query za 10s za urcitu dobu?):
    SeomozException: HTTP Error 503: Service Unavailable: Back-end server is at capacity
- error: [Errno 32] Broken pipe - problem ked sa caka na SEOMoz vysledok a vlakno spracovavajuce poziadavky sa zrusi => riadne otestovat click-festom
- Google:
  - hl (host language) - interface language of user's interface,
  odhaduje jazyk vysledkov na zaklade klucovych slov      -
  - lr (language restrict) - documents written in particular language,
  may affect XML search results, especially on international queries
  when language restriction (using the lr parameter) is not explicitly
  specified
