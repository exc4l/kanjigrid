import kanjigrid

gridder = kanjigrid.Gridder("Kanji", 40, "Header", 52)
grading = kanjigrid.Jouyou()

with open("test.txt", "r", encoding="utf-8") as f:
    data = f.read()

gridder.feed_text(data)
grid = gridder.make_grid(grading, outside_of_grading=True, stats=True, bar_graph=True)
grid.save("test.png")
if "𠮟" in grading.get_all_in_grading():
    print("𠮟")
if "塡" in grading.get_all_in_grading():
    print("塡")
if "叱" in grading.get_all_in_grading():
    print("叱 as replacement")