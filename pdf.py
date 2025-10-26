from fpdf import FPDF
from fpdf import Template
#HEADER FOOTER:
class FPDF(FPDF):

    def header (self):
        self.set_font("arial", "B", 14)
        self.image("Banorte-logo.jpg", h=20)
        self.set_xy(10,30)

    def footer (self):
        self.set_y(-20)
        pageNum = self.page_no()
        self.cell(0,10,f"{self.footer_text}     {str(pageNum)}", "Top" ,align="R")
        self.rect()

def pdf_builder(No_colonias: int, responses : list):

    colonias_Nom = ["escobedo", "roma", "roma2 ", "roma3", "roma4"]

    #PDF SETUP
    pdf = FPDF("p", "mm", "A4") #orientacion, Unidad de medida, dimensiones puede ser en format=(x,y)

    W = 210 #legal: 215.9 A4: 210
    H = 297 #legal: 355.6 A4: 297
    border = True

    pdf.set_font("arial", "", 14)
    pdf.set_margins(10, 10, 10)
    pdf.add_page()


    #page 1
    pdf.set_font("arial", "B", 16)
    pdf.set_xy(10,40)
    pdf.cell(0,10,"this is the title", border ,align="C")

    pdf.set_font("arial", "", 12)
    pdf.set_xy(15,70)
    pdf.cell(0,35,"this is the Introduction", border)

    pdf.set_font("arial", "B", 14)
    pdf.set_xy(10,120)
    pdf.cell(0,10,"Index", border)

    Index_Y = 135
    pdf.set_font("arial", "", 12)
    pdf.set_xy(15, Index_Y)
    Index_Y_step = (H-20-Index_Y)/No_colonias

    for i in range(No_colonias):
        pdf.set_xy(15, Index_Y+Index_Y_step*i)
        pdf.cell(0, 10, f"- {colonias_Nom[i]}") #COLONIAS NOM NO EXISTE AUN
        pdf.set_xy(W*0.75, Index_Y+Index_Y_step*i)
        pdf.cell(0, 10, f"pg. {i+2}")

    #page n
    for i in range (No_colonias):
        pdf.add_page()

        pdf.set_font("arial", "B", 14)
        pdf.cell(0,10,"Neighbourhood name", border)
        pdf.set_font("arial", "", 12)
        pdf.set_xy(15,50)
        #pdf.cell(0,35,"Neighbourhood one text", border)
        pdf.multi_cell(0,7,(responses[i]).text,border)
        pdf.set_xy(15,140)
        img_sz = 100
        pdf.image("spong.png", w=img_sz, x= (W-img_sz)/2 )

    
    

    pdf.output("tutorial.pdf")


#syntasis/doc:
#CELL
#cell(width, height, "text", border type, ln, align="l")
#width = 0 takes all the line from margin to margin
#border type: 1 = alrededor, "l", "r", "T", "B"
#ln 1 skips line after cell, ln 0 continues same line, ln 2 puts cursor under cell
#align = l, l = left, C = center, R = right
#fill = True, fils with colors, False default
#link = "link" text becomes link

#SET, sets the cursor at position x,y
#pdf.set_xy(x,y)

#Multi_cell, cell but multi line and text adjusts to width 
#pdf.multi_cell(w,h, txt= text, border= 1)
#h = height of a cell not container
#same ¿all? parameters as normal cell

#HEADER, define a class

#SHAPES
#pdf.elipse(x,y,d1,d2,style="FD") D=draw border, F= fill, FD both
#pdf.rect(x,y,l1,l2,style"DF")
#pdf.line(x,y,x1,y1)
#pdf.dashed_line(x1,y1,x2,y2, dash_lenght = n, space_lenght = n)

#COLOR:
#pdf.set_text_color(R,G,B)
#pdf.set_draw_color(R,G,B) for borders not fills
#pdf.set_fill_color(R,G,B) for shapes and cell colors

#IMAGES
#pdf.image("filename", w=width, h= height, x = xpos, y = ypos ))
#filename =  if file in folder or direction
#width and height, if only one defined second is adjusted automatically
#x pos and y pos
#can be added to header or foot

#class FPDF(FPDF):
# def header (self):
#   self.set_font()
#   self.cell()
#   self.set_xy(x,y)

# def footer (self):
#   pass