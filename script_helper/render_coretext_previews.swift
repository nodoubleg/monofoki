// Render actual fallback glyphs, using same-run font files, without installing them.
// swift script_helper/render_coretext_previews.swift CATALOG REGULAR.otf NERD.otf OUTPUT
import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
import CryptoKit

let args = CommandLine.arguments
guard args.count == 5 else { fatalError("Expected catalogue, regular OTF, Nerd OTF, output directory") }
let catalog = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: args[1]))) as! [String: Any]
let expectedHashes = catalog["font_sha256"] as! [String: String]
let targets = catalog["fallback"] as! [[String: Any]]
let output = URL(fileURLWithPath: args[4], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
let cell = 128, columns = 16
var records: [[String: Any]] = []
var counts: [String: Int] = [:]
for (variant, argument) in [("regular", args[2]), ("nerd", args[3])] {
    let url = URL(fileURLWithPath: argument)
    let digest = SHA256.hash(data: try Data(contentsOf: url)).map { String(format: "%02x", $0) }.joined()
    precondition(digest == expectedHashes[variant], "Font input hash mismatch")
    var error: Unmanaged<CFError>?
    guard CTFontManagerRegisterFontsForURL(url as CFURL, .process, &error) else { fatalError("Registration failed: \(String(describing: error))") }
    let descriptors = CTFontManagerCreateFontDescriptorsFromURL(url as CFURL) as! [CTFontDescriptor]
    let font = CTFontCreateWithFontDescriptor(descriptors[0], 58, nil)
    let entries = targets.filter { !($0[variant] as! Bool) }
    counts[variant] = entries.count
    let height = max(cell, ((entries.count + columns - 1) / columns) * cell)
    for theme in ["dark", "light"] {
        let context = CGContext(data: nil, width: cell * columns, height: height, bitsPerComponent: 8, bytesPerRow: 0,
                                space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
        let color = theme == "dark" ? CGColor(red: 236/255, green: 235/255, blue: 240/255, alpha: 1) : CGColor(red: 32/255, green: 31/255, blue: 38/255, alpha: 1)
        for (index, item) in entries.enumerated() {
            let hex = item["codepoint"] as! String
            let cp = UInt32(hex, radix: 16)!
            let text = String(UnicodeScalar(cp)!) // Bare scalar: no normalization or variation selector.
            let attributed = NSAttributedString(string: text, attributes: [NSAttributedString.Key(kCTFontAttributeName as String): font,
                                             NSAttributedString.Key(kCTForegroundColorAttributeName as String): color])
            let line = CTLineCreateWithAttributedString(attributed)
            let runs = CTLineGetGlyphRuns(line) as! [CTRun]
            let usedFonts = runs.map { run -> String in
                let properties = CTRunGetAttributes(run) as NSDictionary
                return CTFontCopyPostScriptName(properties[kCTFontAttributeName] as! CTFont) as String
            }
            let missing = runs.isEmpty || runs.contains { run in
                let properties = CTRunGetAttributes(run) as NSDictionary
                let used = properties[kCTFontAttributeName] as! CTFont
                var glyphs = [CGGlyph](repeating: 0, count: CTRunGetGlyphCount(run))
                CTRunGetGlyphs(run, CFRange(location: 0, length: 0), &glyphs)
                return (CTFontCopyPostScriptName(used) as String).contains("LastResort") || glyphs.first == 0
            }
            let x = (index % columns) * cell, top = (index / columns) * cell
            context.saveGState()
            context.clip(to: CGRect(x: x, y: height - top - cell, width: cell, height: cell))
            let bounds = CTLineGetBoundsWithOptions(line, [.useGlyphPathBounds])
            context.textPosition = CGPoint(x: CGFloat(x + cell / 2) - bounds.midX, y: CGFloat(height - top - cell / 2) - bounds.midY)
            CTLineDraw(line, context)
            context.restoreGState()
            if theme == "dark" {
                records.append(["codepoint": hex, "name": item["name"]!, "variant": variant, "input": [hex],
                                "fonts": usedFonts, "missing": missing, "x": x, "y": top])
            }
        }
        let file = output.appendingPathComponent("\(variant)-\(theme).png")
        let destination = CGImageDestinationCreateWithURL(file as CFURL, UTType.png.identifier as CFString, 1, nil)!
        CGImageDestinationAddImage(destination, context.makeImage()!, nil)
        guard CGImageDestinationFinalize(destination) else { fatalError("PNG encoding failed") }
    }
    CTFontManagerUnregisterFontsForURL(url as CFURL, .process, nil)
}
#if arch(arm64)
let hostArchitecture = "arm64"
#elseif arch(x86_64)
let hostArchitecture = "x86_64"
#else
let hostArchitecture = "other"
#endif
let report: [String: Any] = ["schema_version": 1, "renderer": "CoreText", "presentation": "native",
                           "macos": ProcessInfo.processInfo.operatingSystemVersionString,
                           "architecture": hostArchitecture,
                           "created": ISO8601DateFormatter().string(from: Date()), "font_sha256": expectedHashes,
                           "font_size": 58, "scale": 2, "cell": cell, "columns": columns,
                           "normalization": "none", "language": "system default", "background": "transparent",
                           "palette": ["dark": "#ECEBF0", "light": "#201F26"], "counts": counts, "records": records]
try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys]).write(to: output.appendingPathComponent("coretext.json"))
print("CoreText snapshot: \(counts), \(records.filter { $0["missing"] as! Bool }.count) missing; \(ProcessInfo.processInfo.operatingSystemVersionString)")
