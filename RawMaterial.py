class Raw_Material:
    def __init__(self,dimensions,raw_material):
        self.dimensions=dimensions
        self.raw_material=raw_material

    def calculate_rcc(self):
        # 1cbm RCC: volumes 0.12 steel/ 1 cement/ 2 sand / 3 gravel / Wasser: 0.5*vol_cement*(3.1/1)  wasserzementwert
        #0.12+1+2+3+0.5*3.1=7.67 #(0,12/7.67)*7850=122kg steel per cbm
        rcc_vol=self.dimensions["structure_vol"]
        steel_weight=rcc_vol*(0.12/7.67)*7850
        cement_weight=rcc_vol*(1/7.67)*2800      #pcement: 2800 kg/cbm
        sand_vol=rcc_vol*(2/7.67)
        gravel_vol=rcc_vol*(3/7.67)

        steel_price=steel_weight*self.raw_material["steel"]
        cement_price=cement_weight*self.raw_material["cement"]
        sand_price=sand_vol*self.raw_material["sand"]
        gravel_price=gravel_vol*self.raw_material["gravel"]
        rcc_price=steel_price+cement_price+sand_price+gravel_price
        rcc_misc_material=rcc_price*(0.135+0.095) #13,5% Formwork wood, 9,5% (threaded) steel rods
        return rcc_price+rcc_misc_material

    def calculate_cc(self):
        # 1 cbm cc: 1 cement / 3 sand / 5 gravel /Wasser: 0.5*vol_cement*(3.1/1)  wasserzementwert
        cc_vol=self.dimensions["structure_vol"]
        cement_weight = cc_vol * (1 / 10.55) * 3100  # pcement: 3100 kg/cbm
        sand_vol = cc_vol * (3/10.55)
        gravel_vol = cc_vol * (5/10.55)

        cement_price = cement_weight * self.raw_material["cement"]
        sand_price = sand_vol * self.raw_material["sand"]
        gravel_price = gravel_vol * self.raw_material["gravel"]
        cc_price = cement_price + sand_price + gravel_price
        return cc_price

    def calculate_masonry(self):
        mas_vol=self.dimensions["structure_vol"]
        brick_vol=mas_vol*0.95
        cement_weight=mas_vol*0.05*0.2*2800
        sand_vol=mas_vol*0.05*0.8
        surface_cement_weight=self.dimensions["contact_sqm"]*0.02*3100 #2cm layer of cement finish

        brick_price=brick_vol*self.raw_material["bricks"]
        cement_price=(surface_cement_weight+cement_weight)*self.raw_material["cement"]
        sand_price=sand_vol*self.raw_material["sand"]
        mas_price = brick_price+cement_price + sand_price
        return mas_price