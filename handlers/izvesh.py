from aiogram import Router
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from docxtpl import DocxTemplate
from states.izvesh import IzveshForm

router = Router()

@router.message(IzveshForm.fio_patient)
async def process_fio_patient(message: Message, state: FSMContext):
    await state.update_data(fio_patient=message.text.strip())
    # Для простоты сразу формируем документ
    data = await state.get_data()
    data["institution"] = "ДКЦ им. Л.М. Рошаля"
    
    try:
        template = DocxTemplate("templates/izvesh.docx")
        template.render(data)
        filename = f"izvesh_{message.from_user.id}.docx"
        template.save(filename)
        await message.answer_document(FSInputFile(filename), caption="✅ Документ успешно сформирован.")
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка при создании документа.")
    await state.clear()
