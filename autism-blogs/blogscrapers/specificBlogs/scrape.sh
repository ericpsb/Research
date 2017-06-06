folders=($(ls -1 Done))
for f in "${folders[@]}"; do
  echo "scraping $f:"
  c1='scrapy runspider Done/'
  c2='/scraper.py -o Done/'
  c3='/data.json'
  echo "$c1$f$c2$f$c3" | bash
done

folders=($(ls -1 Stray))
for f in "${folders[@]}"; do
  echo "scraping $f:"
  c1='scrapy runspider Stray/'
  c2='/scraper.py -o Stray/'
  c3='/data.json'
  echo "$c1$f$c2$f$c3" | bash
done