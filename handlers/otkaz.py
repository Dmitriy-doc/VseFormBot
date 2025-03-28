from aiogram import Router
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from docxtpl import DocxTemplate
from states.otkaz import OtkazForm

router = Router()

@router.message(OtkazForm.fio_patient)
async def process_fio_otkaz(message: Message, state: FSMContext):
    await state.update_data(fio_patient=message.text.strip())
    data = await state.get_data()
    data["institution"] = "ДКЦ им. Л.М. Рошаля"
    
    try:
        template = DocxTemplate("templates/otkaz.docx")
        template.render(data)
        filename = f"otkaz_{message.from_user.id}.docx"
        template.save(filename)
        await message.answer_document(FSInputFile(filename), caption="✅ Документ успешно сформирован.")
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка при создании документа.")
    await state.clear()
