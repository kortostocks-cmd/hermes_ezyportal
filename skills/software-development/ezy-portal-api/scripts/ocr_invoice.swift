import Cocoa
import Vision

guard CommandLine.arguments.count > 1 else {
    print("Usage: swift ocr_invoice.swift <image_path>")
    exit(1)
}

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)
guard let image = NSImage(contentsOf: url),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("Error: Cannot load image at \(path)")
    exit(1)
}

let request = VNRecognizeTextRequest { request, error in
    if let error = error {
        print("Error: \(error)")
        exit(1)
    }
    guard let observations = request.results as? [VNRecognizedTextObservation] else {
        print("No results")
        exit(0)
    }
    let texts = observations.compactMap { $0.topCandidates(1).first?.string }
    for text in texts {
        print(text)
    }
    exit(0)
}
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false

try? VNImageRequestHandler(cgImage: cgImage, options: [:]).perform([request])
RunLoop.current.run(until: Date(timeIntervalSinceNow: 30))