class ImageLoadingException(Exception):
    def __str__(self):
        return "Image loading error"

class QRNotFoundException(Exception):
    def __str__(self):
        return "QR code not found"

class ImageProcessingException(Exception):
    def __str__(self):
        return "Image processing error"

class QRCodeIncorrectException(Exception):
    def __str__(self):
        return "QR code incorrect"

class ARUCONotFoundException(Exception):
    def __str__(self):
        return "ARUCO not found"

