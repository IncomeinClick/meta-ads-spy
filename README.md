# meta-ads-spy

Skill โบนัสจากคอร์ส **จ้างเอไอยิง Meta Ads** — ให้ AI/Newton ของคุณ **ส่องโฆษณาคู่แข่งจริงใน Meta Ad Library** แล้วต่อยอดเป็นไอเดียคอนเทนต์ยิงแอดให้ในแชทเดียว

หลักคิดของ media buyer มืออาชีพ: ก่อนคิดคอนเทนต์ ให้ดูก่อนว่าคู่แข่งตัวไหน "ยิงแล้วได้ผล" (= ยิงต่อเนื่องมานาน) แล้วปั้นมุมที่ต่างแต่แข่งได้

---

## 1. ติดตั้ง (ครั้งเดียว)

บอก Newton/AI ของคุณว่า:

> ติดตั้ง skill จาก repo นี้ให้หน่อย: https://github.com/IncomeinClick/meta-ads-spy

หรือรันเองในเครื่อง:

```bash
git clone https://github.com/IncomeinClick/meta-ads-spy.git ~/.claude/skills/meta-ads-spy
```

> Newton อ่าน skill จาก `~/.claude/skills/` (เชื่อมไป `~/.agents/skills/`) — clone ลงโฟลเดอร์นั้นแล้วใช้ได้เลย

## 2. ตั้งค่า Meta token (ครั้งเดียว)

Skill ดึงข้อมูลจาก **Meta Ad Library API** ต้องใช้ token ของคุณเอง:

1. **ยืนยันตัวตน** ที่ [facebook.com/id](https://facebook.com/id) — อัปบัตรประชาชน/พาสปอร์ต รอ 1-3 วันทำการ (ทำครั้งเดียว ใช้ได้ตลอด)
2. สร้าง Facebook App ของตัวเอง + สร้าง **access token แบบ long-lived** (อยู่ได้ ~60 วัน)
3. เก็บ token ไว้:
   ```bash
   mkdir -p ~/.config/meta-ads-spy
   printf '%s' 'ใส่_TOKEN_ของคุณ' > ~/.config/meta-ads-spy/token
   ```
   (หรือ set env `META_ADS_TOKEN`)

> ขั้นตอนสร้าง app + token มีสอนละเอียดในคอร์ส (บท connect)

## 3. ใช้งาน

พิมพ์สั่งเป็นภาษาคนได้เลย เช่น:

> ช่วยคิดคอนเทนต์ยิงแอด **[สินค้าของคุณ]** ให้หน่อย

Newton จะ: ถามสินค้า/คู่แข่ง → ส่อง Ad Library หาแอดที่ยิงนาน (winner) → สรุปว่าคู่แข่งเล่นมุมไหน → เสนอ big idea ที่ต่างแต่แข่งได้ → (พอคุณโอเค) ร่างคอนเทนต์ให้เลย

---

## โครงสร้าง
- `SKILL.md` — protocol การทำงาน (สิ่งที่ AI อ่าน)
- `scripts/adlib_search.py` — ตัวยิง Ad Library API (Python 3, ใช้ stdlib ล้วน ไม่ต้องลงอะไรเพิ่ม)

## หมายเหตุ
- ถ้าขึ้น `identity_not_confirmed` = ยังไม่ผ่านขั้นตอนที่ 2.1 (รอ Meta อนุมัติก่อน)
- ถ้าขึ้น `token_expired` = สร้าง token ใหม่แล้วอัปเดตไฟล์ token
- รองรับตลาดไทย (default) และต่างประเทศ (ระบุ country ได้)
