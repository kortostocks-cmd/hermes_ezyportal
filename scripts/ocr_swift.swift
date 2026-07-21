import Cocoa
import Vision
import Dispatch

func ocrImage(_ path: String) -> String {
    let url = URL(fileURLWithPath: path)
    var result = ""
    let sem = DispatchSemaphore(value: 0)
    
    guard let image = NSImage(contentsOf: url), let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        return "ERROR: No se pudo cargar la imagen"
    }
    
    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            result = "ERROR: \(error.localizedDescription)"
            sem.signal()
            return
        }
        guard let observations = request.results as? [VNRecognizedTextObservation] else {
            result = "No se encontró texto"
            sem.signal()
            return
        }
        let texts = observations.compactMap { $0.topCandidates(1).first?.string }
        result = texts.joined(separator: "\n")
        sem.signal()
    }
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    
    try? VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
    sem.wait()
    return result
}

// Accept image path as argument
let args = CommandLine.arguments
if args.count >= 2 {
    let path = args[1]
    print(ocrImage(path))
} else {
    print("ERROR: Uso: ocr_swift <ruta_imagen>")
}