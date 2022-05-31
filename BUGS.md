# Bugs
+ ~~bug#1: Если в конфигурации несколько тегов с одним адресом в драйвере модбас созддается несколько одинаковых запросо~~ 
 [**screen1**](doc/screens/bugs/screen1.png)
+ bug#2: It's same as before (bug#1) but for adding from context menu OIServerViewer
  [**screen2**](doc/screens/bugs/screen2.png)
This fix should do in Device.addRange. This method should itself reallocate the ranges based on the existing ranges.
+ OIServerViewer: если добавить тег, то после сохранения SaveAs оне нед добавляется в конфигурацию.
+ 