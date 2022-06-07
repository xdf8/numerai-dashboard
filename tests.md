# Tests

In diesem Test werden folgende Äquivalenzklassen überprüft:
- Slider
- Multiselect
- Checkbox
- Selectbox


---

# ÜBERHAUPT NÖTIG?
Das Dashboard wurde mit Hilfe des Frameworks [Streamlit](https://streamlit.io) erstellt. 

---

## Slider

**in nachfolgenden tests ist die erwartung...**

Mit hilfe des Sliders kann in diesem Testfall die Runde des Numerai Tournaments ausgewählt werden, ab der die Auswertung gestartet werden soll. Die erste Runde ist 284, die letzte 318 (Stand 07.06.2022).

In nachfolgenden Tests ist die Erwartung, dass ab einer Auswahl von Runde 307 oder höher keine Werte mehr für das Modell *kenfus* existieren. Dieses Modell wurde das letzte mal in Runde 306 verwendet.

![slider](tests/screenshots/slider_round_284.png)
##### Fig.1 - Slider und Graph mit Auswahl Runde 284


Wenn man den Wert des Sliders anpasst, sollte sich auch der Plot verändern.

![slider](tests/screenshots/slider_round_306.png)
##### Fig.2 - Slider und Graph mit Auswahl Runde 306


Da in Runde 306 noch alle 4 Modelle existieren, verändert sicht hier nur der Plot. Auch ist durch die Verbesserung der Werte zu sehen, dass die Modelle weiter entwickelt worden sind.

![slider](tests/screenshots/slider_round_306.png)
##### Fig.3 - Slider und Graph mit Auswahl Runde 307


Wie zu erwarten ist ab Runde 307 erscheint das Modell *kenfus* nicht mehr im Plot. Der Slider funktioniert also korrekt