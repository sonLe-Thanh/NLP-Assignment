# BÀI TẬP LỚN XỬ LÝ NGÔN NGỮ TỰ NHIÊN
Author: Lê Thành Sơn - 1810481
## REQUIREMENTS
Cần cài đặt VietCoreNLP để kích hoạt module tokenizer.
```
pip install vncorenlp
```

## DATA
Các file data bao gồm:
* BusName.txt: chứa tên các chuyến bus.
* city.txt: chứa tên các thành phố.
* data.txt: chứa dữ liệu được cung cấp.
* equivalent.txt: chứa dữ liệu về các cặp từ tương đối gần nghĩa, dùng để convert cho thuận tiện.
* relations.txt: chứa dữ liệu về mối quan hệ giữa các cặp từ trong câu, nếu quan hệ chưa được cập nhật, có thể dẫn đến sai sót khi thực hiện
* các folder còn lại có sẵn khi cài đặt [vncorenlp theo hướng dẫn](https://github.com/vncorenlp/VnCoreNLP).
## CONTENTS
### Cách thực hiện
Các câu được nhập vào sẽ được chuyển về các từ đồng nghĩa để tạo ra một câu có nghĩa gần tương đương dựa trên file data,
sau đó sẽ tiến hành thay đổi thời gian, thêm động từ nếu thiếu để chuẩn hoá dạng của câu trước khi thực hiện.

Sau đó, nội dung câu sẽ được thực hiện lần lượt theo các bước bởi các hàm đã hiện thực.
### Sử dụng
```
python main.py <file input.txt>
```
Trong đó file input.txt là một file text được để trong folder Input, 
chỉ cần nhập tên file, không cần dùng đường dẫn tuyệt đối.

Tác giả đã chuẩn bị sẵn file 1.txt gồm các câu có thể dùng được có thể được dùng bằng lệnh:
```
python main.py 1.txt 
```
Các kết quả được lưu trong các file text trong folder Output.
### Các dạng câu hỗ trợ 
Các câu hỏi có dạng 
> Xe buýt nào từ Đà Nẵng lúc 8:30 HR đến thành phố Hồ Chí Minh lúc 18:30 HR?

> Xe buýt nào đến thành phố Hồ Chí Minh lúc 18:30 HR?

> Xe buýt nào đến lúc 19:00 HR?

> Xe buýt nào đến Huế từ Hà Nội ?

> Xe buýt B1 đi từ đâu?

> Xe buýt B2 đi đến đâu?

> Xe buýt B5 đi từ lúc nào đến lúc nào?

> Chuyến xe nào xuất phát từ thành phố đáng sống đến thủ đô của Việt Nam ?

> Xe bus nào lăn bánh tới Huế lúc 10 giờ rưỡi tối ?

Đối với các câu hỏi dạng tìm thời gian đi, có thể sử dụng các dạng:
> Thời gian xe buýt B3 từ Đà Nẵng đến Huế ?

> Xe buýt B1 đi hết bao lâu?

Các từ hỏi khi dùng dạng này cần đúng chuẩn để đảm bảo ít lỗi (dùng từ Thời gian/hết bao lâu).

Ngoài ra, bài làm cũng hỗ trợ việc thay đổi thời gian dạng quen thuộc của người Việt (dùng từ 9 giờ rưỡi tối/sáng/chiều/khuya/trưa).

## Một số lỗi
- Đôi khi một số file có thể lỗi khi mở.
- Các câu hỏi có thể gặp lỗi lúc parsing nếu dấu ? dính vào từ cuối cùng trong câu.
- Đối với các cặp từ chưa được thể hiện trong file, bài làm sẽ không thể thực hiện.
## Hạn chế
* Chưa hỗ trợ tất cả các dạng COMMAND, Y/N Question.
* Dữ liệu chưa được cập nhật đầy đủ.
