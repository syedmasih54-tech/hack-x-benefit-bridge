export async function checkImageQuality(file: File) {
  const bitmap = await createImageBitmap(file)
  if (bitmap.width < 720 || bitmap.height < 480) {
    bitmap.close()
    return "छवि बहुत छोटी है। कृपया पास से दोबारा लें।"
  }

  const canvas = document.createElement("canvas")
  const size = 120
  canvas.width = size
  canvas.height = size
  const context = canvas.getContext("2d", { willReadFrequently: true })
  if (!context) {
    bitmap.close()
    return null
  }

  context.drawImage(bitmap, 0, 0, size, size)
  bitmap.close()
  const { data } = context.getImageData(0, 0, size, size)
  let brightness = 0
  let edge = 0
  for (let i = 0; i < data.length; i += 4) {
    brightness += (data[i] + data[i + 1] + data[i + 2]) / 3
    if (i >= 4) edge += Math.abs(data[i] - data[i - 4])
  }
  brightness /= data.length / 4
  edge /= data.length / 4
  if (brightness < 45) return "छवि बहुत अंधेरी है। अधिक रोशनी में दोबारा लें।"
  if (edge < 7) return "छवि धुंधली लग रही है। कैमरा स्थिर रखकर दोबारा लें।"
  return null
}

export function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}
