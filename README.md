# Build network topology on SDN using Mininet and OpenDaylight

## Start the server
  1. Chạy ODL trên Ubuntu
     ```
     cd distribution-karaf-0.6.4-Carbon
     ./bin/karaf
     ```
  2. Chạy mininet với file `topo.py` mô tả các liên kết trong mạng
     ```
     sudo mn --custom topo.py --topo sdntopo –mac --controller=remote,ip=[odl-ip] --switch ovs,protocols=OpenFlow13 
     ```
  3. Tạo folder `venv` và cài đặt các thư viện trong file `requirements.txt`
     ```
     cd server
     python -m venv venv
     source venv/Scripts/activate
     pip3 install -r requirements.txt
     ```
  4. Thay đổi ODL-IP của `BASE_URL` trong `server/config.py`
  5. Start the server:
     ```
     cd ..
     ./run.sh
     ```
