import torch
import whisper

# Загрузка модели
model = whisper.load_model("turbo")

# Подготовка модели для квантования
model.eval()  # Перевод модели в режим оценки (обязательно для квантования)

# Динамическое квантование
quantized_model = torch.quantization.quantize_dynamic(
    model,  # Модель
    {torch.nn.Linear},  # Слои, которые подвергаются квантованию
    dtype=torch.qint8  # Тип данных для квантования
)

# Сохранение квантованной модели
torch.save(quantized_model.state_dict(), "quantized_whisper_model.pth")
