# 8-Bit Computer IDE
Sıfırdan yaptığım 8-bit bilgisayarın IDE ve assembler ı.

- IDE yi tamamen sıfırdan Python kullanarak yazdım ve yazıyorum. 1 kişi için gerçekten büyük bir projedir ve dosyalar paketlenmiş ve moduler olarak yazılmış olsada çok fazladır.

- Bağlantı kesildiğinde otomatik anlar.

- VENV ve GitHub kullanır böylece her bilgisayarda kolayca yüklenebilir ve programlanabilir.

- Bütün kod modullere ayrılmıştır. Assembler, GUI ve asıl program birbirinden ayrılmıştır.(herbiri "editable" modunda venv içine yüklüdür)

- Assembler kodu yazılmıştır. Moduler olarak yazılmıştır ve çok kolay olarak yeni 8-bit bilgisayar komutları eklenebilir veya modifiye edilebilir.

- Sıfırdan tokenizer, parser ve kod oluşturucular yazılmıştır. Normal bir assembler veya derleyici gibi her türlü yazım hatasını farkeder, ve hangi satır ve stünda hata olduğunu gösterir.

- Assembler "Intel .hex" standardını kullanır. Hex dosyaları standarda uygun yazılır ve her kodun sonuna otomatik "HALT" komudu konur.(8-bit bilgisayarın kod sonuna geldiğinde daha ileri gitmemesi için)

- Hex kodu tamamen 8-bit bilgisayar platformu için sıfırdan yazılmıştır ve kod 64kB dan fazla gibi durumlarda gerekli hatayı verir.

- Disassembler da yazılmıştır. Oluşturulan hex dosyasından gerekli opcode ve değer sayılarını çıkarır ve assembly kodunu yeniden oluşturur.

- Aynı şekilde hex dosyasındaki komutları görmek için "view" komudu yazılmıştır. Hex dosyasından herhangi addresteki herhangi komudu gösterebilir.

- Programlayıcı direk, bir GUI olmadan terminal üzerinden çalışabilir. Asıl arayüz "interface" paketi olarak geçer ve "__main__.py" dosyası vardır, yani "-m" kullanılarak direk terminalden kullanılabilir.(VS Code üzerinde "Task" olarak kuruludur)

- Tkinter kullanılarak bu programa GUI oluşturuyorum ve şuanlık yapım aşamasında. Direk "interface" modülünü kullanır ve yanına "cls" gibi ekran temizleme kodları ekler.

- GUI direkt olarak proje klasöründeki "main.py" dosyası kullanılarak hızlıca test edilebilir.(VS Code üzerinde "Task" olarak kuruludur)

- GUI Pyinstaller kullanılarak exe programı olarak oluşturulabilir. Bunun için proje klasöründeki "build.py" dosyası kullanılır ve her türlü ayarı otomatik yapar.(VS Code üzerinde "Task" olarak kuruludur)

- Exe dosyası "executable/dist/Custom 8-Bit Computer IDE.exe" dir.

- IDE "config.cfg" dosyası kullanarak ayarlarını kaydeder ve yükler, böylece kullanıcı IDE ayarlarını değiştirip kapatırsa, yeniden açtığında ayarlar geri yüklenir. "build.py" gerekli dosyların transferini otomatik yapar.

- Hala yapım aşamasındadır ve ileride tam donanımlı bir IDE olmasını planlıyorum.


<img src="./Resimler/VS Code Resim.jpg" width="500">

# IDE resimleri:
<p float="left">
  <img src="./Resimler/GUI Resim-1.jpg" width="500">
  <img src="./Resimler/GUI Resim-2.jpg" width="500">
</p>






