from flask import Flask, render_template, request, make_response
import pdfkit
import base64
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.form
    def get_val(key): return data.get(key, '')
    
    sig_customer = get_val('signature_customer')
    sig_chief = get_val('signature_chief')

    war_during = "[ &#10004; ]" if get_val('warranty') == "อยู่ในช่วงรับประกัน (During)" else "[&nbsp;&nbsp;&nbsp;]"
    war_notin = "[ &#10004; ]" if get_val('warranty') == "ไม่อยู่ในช่วงรับประกัน (Not in)" else "[&nbsp;&nbsp;&nbsp;]"
    stat_done = "[ &#10004; ]" if get_val('status') == "งานเสร็จ/ Completed" else "[&nbsp;&nbsp;&nbsp;]"
    stat_notdone = "[ &#10004; ]" if get_val('status') == "งานยังไม่เสร็จ/ Not completed yet" else "[&nbsp;&nbsp;&nbsp;]"

    # แปลงรูปโลโก้
    logo_path = os.path.join('static', 'logo.png')
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')

    # ระบบจัดการรูปถ่าย (ก่อนซ่อม / หลังซ่อม)
    pic_before = request.files.get('pic_before')
    pic_after = request.files.get('pic_after')

    def get_img_b64(file_obj):
        if file_obj and file_obj.filename != '':
            # อ่านไฟล์รูปแล้วแปลงเป็น Base64
            return "data:image/jpeg;base64," + base64.b64encode(file_obj.read()).decode('utf-8')
        return ""

    b64_before = get_img_b64(pic_before)
    b64_after = get_img_b64(pic_after)

    img_tag_before = f'<img src="{b64_before}" style="max-width: 100%; max-height: 250px; display: block; margin: 0 auto;">' if b64_before else '<br><br>-- ไม่ได้แนบรูป --'
    img_tag_after = f'<img src="{b64_after}" style="max-width: 100%; max-height: 250px; display: block; margin: 0 auto;">' if b64_after else '<br><br>-- ไม่ได้แนบรูป --'

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Tahoma, sans-serif; font-size: 12px; margin: 0; padding: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: -1px; }}
            th, td {{ border: 1px solid #000; padding: 5px; vertical-align: top; }}
            .red-text {{ color: red; font-weight: bold; }}
            .header-text {{ text-align: center; font-size: 16px; font-weight: bold; margin: 5px 0; }}
            .sig-img {{ width: 140px; border-bottom: 1px solid #000; }}
        </style>
    </head>
    <body>
        <table>
            <tr>
                <td width="25%">
                   <img src="{logo_b64}" style="width: 250px; height: auto; display: block; margin: 0 auto;" alt="Logo">
                </td>
                <td width="50%">
                    <p class="header-text">ใบรายการซ่อมเครื่อง</p>
                    <p class="header-text">Service Report</p>
                    ชื่อลูกค้า / Customer: {get_val('customer')}<br><br>
                    ซื้อจาก / seller: {get_val('seller')}
                </td>
                <td width="25%" style="font-size: 14px; line-height: 1.4;">
                    ukoset@ksc.th.com<br>Tel : 02-159-6391-3<br>
                    <hr style="border: 0.5px solid #000; margin: 5px 0;">
                    วันที่ / Date: {get_val('date')}<br>
                    เข้าซ่อมครั้งที่/service time(s): {get_val('service_times')}<br>
                    <span class="red-text" style="font-size: 16px;">หมายเลข / SR- {get_val('sr_no')}</span>
                </td>
            </tr>
        </table>

        <table>
            <tr>
                <td width="35%">
                    เครื่อง/ Machine: {get_val('machine')}<br>
                    ยี่ห้อ/(Brand): {get_val('brand')}<br>
                    รุ่น/Model: {get_val('model')}<br>
                    หมายเลขเครื่อง/Serial No.: {get_val('serial_no')}
                </td>
                <td width="30%">
                    วันที่รับเครื่อง/ Delivery date: {get_val('delivery_date')}<br>
                    <hr style="border: 0.5px solid #000;">
                    สถานะการรับประกัน/ warranty:<br>
                    {war_during} อยู่ในช่วงรับประกัน (During)<br>
                    {war_notin} ไม่อยู่ในช่วงรับประกัน (Not in)
                </td>
                <td width="35%">
                    อาการเสียเบื้องต้น / Breaking Down:<br>
                    {get_val('breakdown').replace(chr(10), '<br>')}
                    <br><br>
                    <hr style="border: 0.5px solid #000; margin: 5px 0;">
                    อาการเสียเมื่อช่างไปถึง / Actual Breaking Down:<br>
                    {get_val('breakdown_actual').replace(chr(10), '<br>')}
                </td>
            </tr>
        </table>

        <table>
            <tr><td colspan="2" style="text-align: center; background-color: #f9f9f9;"><strong>รายละเอียดการให้บริการหรือซ่อม/ Description of Service or Repair</strong></td></tr>
            <tr>
                <td colspan="2" height="200">{get_val('description').replace(chr(10), '<br>')}</td>
            </tr>
            <tr>
                <td width="50%" height="250" style="text-align: center; vertical-align: middle;">
                    <strong>รูปก่อนซ่อม (Before)</strong><br><br>
                    {img_tag_before}
                </td>
                <td width="50%" height="250" style="text-align: center; vertical-align: middle;">
                    <strong>รูปหลังซ่อม (After)</strong><br><br>
                    {img_tag_after}
                </td>
            </tr>
        </table>

        <table>
            <tr>
                <td width="30%" height="120">ความคิดเห็นจากช่าง/ Recommend:<br>{get_val('recommend').replace(chr(10), '<br>')}</td>
                <td width="40%">รายการอะไหล่/ Spare parts used:<br>{get_val('spare_parts').replace(chr(10), '<br>')}</td>
                <td width="30%">
                    เริ่มงาน: {get_val('start_time')} เสร็จ: {get_val('finish_time')}<br>
                    เวลารวม: {get_val('total_time')}<br>
                    {stat_done} งานเสร็จ<br>
                    {stat_notdone} งานไม่เสร็จ
                </td>
            </tr>
        </table>

        <table>
            <tr><td colspan="2">รายชื่อช่างที่ให้บริการ/ Service name: {get_val('service_names')}</td></tr>
            <tr>
                <td width="50%" style="text-align: center; padding-top: 10px;">
                    <img src="{sig_customer}" class="sig-img"><br>
                    ลงชื่อลูกค้า / Customer
                </td>
                <td width="50%" style="text-align: center; padding-top: 10px;">
                    <img src="{sig_chief}" class="sig-img"><br>
                    หัวหน้าช่าง / Chief Engineer
                </td>
            </tr>
            <tr>
                <td colspan="2" style="text-align: center; font-size: 10px; padding-top: 10px;">
                    ติดต่อสอบถาม 02-159-6391-3 หรือ siameimatechgroup@yahoo.com
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    options = {'page-size': 'A4', 'margin-top': '5mm', 'margin-right': '5mm', 'margin-bottom': '5mm', 'margin-left': '5mm', 'encoding': "UTF-8"}

    pdf = pdfkit.from_string(html_content, False, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=service_report.pdf'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
