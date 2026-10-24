cd ~/Files/IntelligentDithering/
open http://127.0.0.1:1313
mkdir /tmp/hugotest
hugo server --buildFuture -D --cleanDestinationDir --bind 0.0.0.0 --buildDrafts -d /tmp/hugotest/
