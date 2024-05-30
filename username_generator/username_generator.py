def rgb(r, g, b):
    def fRGB(n):
        if n < 0:
            n = 0
        elif n > 255:
            n = 255
            
        if len(hex(n)[2:].upper()) < 2:
            return "0" + hex(n)[2:].upper()
        return hex(n)[2:].upper()
        
    result = fRGB(r) + fRGB(g) + fRGB(b)
    return result

print(rgb(400 ,369 ,801))