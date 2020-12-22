## Ehrenbot: Discords ehrenhaftester Bot!
Ehrenbot ist ein... passiv-aggressiver moderator Bot für Discord Server mit einigen einzigartigen Features!


**Wer oder was ist Ehrenbot?**

Meine Originalidee für Ehrenbot war, einen Discord Bot zu schaffen, welcher einen Server mit einer digitalen Währung namens "Ehre" ausstattet, welche man sich auf unterschiedlichste Art und Weise verdiehnen könnte und die man für Verschiedenes hätte ausgeben können. Während der Entwicklung der ersten Version ist mir allerdings aufgefallen, dass es wesentlich cooler wäre, wenn Ehrenbot die Mitglieder eines Servers anhand ihres Benehmens "bewerten" würde. Somit ist Ehrenbot eine Mischung aus der urspünglichen Idee und einem Moderator Bot geworden, welcher nun jedes Mitglied anhand seines Verhaltens mit Ehre bewertet. 

**Welche Features bietet der Bot?**

* Einführung einer digitalen Währung auf dem Server, welche jedes Mitglied bewertet
  * Mitglieder können täglich jemandem Ehre spenden, Abstimmungen über das Verhalten anderer einrichten, sich ihren Kontoverlauf ansehen und vieles Mehr!
* Verschiedene Admin Kommands, welche Moderatoren das Leben erleichtern
  * optionale Zensierung von Schimpfwörtern im Chat
  * Zugriff auf bestimmte logs
  * Weitere Features in Zukunft!
* Kein kompliziertes Setup notwendig, der Bot richtet alles automatisch ein!
* Viele Einstellungen können für jeden Server individuell angepasst werden
* Easy to use mit Umfassenden Erklärungen
* Antispam System
* Eine Botinstanz kann auf mehreren Server gleichzeitig laufen
* Regelmäßige Updates mit neuen Features!

**Wie füge ich Ehrenbot auf meinem Server hinzu?**

Um Ehrenbot auf einem Server hinzuzufügen, musst du auf dem Server mindestens die Berechtigung "Server Verwalten" haben. Hast du diese, kannst du Ehrenbot ganz einfach über [diesen Link](https://discord.com/api/oauth2/authorize?client_id=733037111258775582&permissions=8&scope=bot "Ehrenbot hinzufügen") hinzufügen! Da der Bot sich in einem frühen Entwicklungsstadium befindet wird er aktuell eher wenig online sein, wenn du ihn dennoch jetzt schon ausprobieren möchtest kannst du mit der unten stehenden Anleitung deine eigene Instanz von Ehrenbot laufen lassen.

**Wie benutze ich Ehrenbot?**

Ehrenbot funktioniert wie fast alle Discord Bots über einen Kommandprefix, der vor jedem Kommand geschrieben werden muss. Die meisten Bots verwenden irgendwelche umständlichen Kombinationen aus Zeichen und Buchstaben als Prefix, Ehrenbot verwendet ganz einfach `ehre`. Um eine Liste aller Kommands zu erhalten musst du einfach nur `ehre help` eingeben und der Bot zeigt dir, was er alles kann.

**Kann ich Ehrenbot auch auf meinem Pc laufen lassen?**

Ja, klar kannst du eine Ehrenbot-Instanz auch auf deinem eigenen Pc laufen lassen. Hierfür benötigst du zunächst einen API Token. Das ist im Prinzip ein privater zugang zu Discord für deinen Bot so wie für dich deine Email und Passwort. Diesen Token bekommst du follgendermaßen:
* Als erstest downloadest du dieses Repository entweder mit git oder indem du auf "Download zip" klickst und den Ordner in einen Ordner deiner Wahl entpackst.
* Du brauchst zudem Python (getestet mit Python 3.7.6), such einfach nach einem Tutorial wie man Pyhton installiert wenn du noch kein Python auf deinem Pc installiert hast und mach dannach hier weiter.
* Als nächstes musst [hier](https://discord.com/developers/) du einen Discord Developer Account erstellen, sofern du noch keinen Besitzt.
* Wenn du deinen Developer Account erstellt hast, klick auf "New Application" um eine neue App für Discord zu erstellen.
* Nachdem die App erstellt wurde, klick auf das Menu "Bot" und dann auf den Button "Add Bot" und dann auf "Yes, do it".
* Nun ist deine App als Bot registriert. Den Token des Bots erhältst du, indem du bei Token neben dem Profilbild des Bots auf "copy token" kilckst. Der Token wird dann in deine Zwischenablage kopiert.
* Nun musst du die Datei "config.json" im heruntergeladenen Ordner öffnen und bei `"token": "TOKEN"` TOKEN durch deinen kopierten Bottoken ersetzen.
* Als letztes musst du einen Einladungslink für den Bot erstellen. Geh hierfür wieder auf die Webseite mit deinem Bot und klick auf "OAuth2". Wähle dann unter "Scopes" Bot aus und im darunter erscheinenden Menu "Bot Permissions" Administrator aus. Dannach kannst du den generierten Einladungslink kopieren und über diesen deine Ehrenbot-Instanz auf deinen Server hinzufügen.
* Der letzte Schritt ist nun, die Datei "Ehrenbot.py" auszuführen. Mach hierfür einfach einen Rechstklick auf die Datei und wähle dann Pyhton zum Öffnen aus.
* Das war's, Ehrenbot sollte alle benötigten Dateien und Discord Kanäle nun automatisch erstellen und du kannst den Bot benutzen!

\
**Geplante Features**

* Einstellung, um unerwünschte Wörter zu Blacklisten, Nachrichten mit diesen Wörtern werden dann gelöscht

**In weiter Zukunft geplante Features**

* Lotterie und weitere Minigames, bei welchen man Ehre setzen muss und Ehre gewinnen kann
* System, um verschiedene Sprachpakete zu verwenden
  * Jedes Pakete enthält alle Nachrichteninhalte, so könnte jeder Server einstellen, ob der Bot z.B. eher Aggressiv oder Freundlich reagiert
  * Pakete für verschiedene Sprachen, neben Deutsch soll irgendwann Englisch unterstützt werden
  
\
\
Solltest du irgendwelche Bugs finden oder willst einfach neue Features vorschlagen, dann erstell ein Ticket und lass es mich wissen!
