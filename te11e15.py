import os
import pandas as pd
import re
import numbers
import sys

list_location=['home','work','other']

list_address=['','','osoite','kaupunki','kunta','postinumero','maa']

def lue_html():
    PAGE = "y:/dev/t1.xhtml"
    yhteystiedot=[]
    tables = pd.read_html(PAGE)
    tables=str(tables)
    tables = re.sub(r"\s+", ",", tables)
    tables=tables.split(',')
    line=''
    linetabl=[]
    for i in tables:
        if not '['  in i and not ']' in i :
            
            on_kokonaisluku = i.isdigit()
            if on_kokonaisluku :
                print(linetabl)
                yhteystiedot.append(linetabl)
                print(line)
                line=''
                linetabl=[]
            else :
                line=line+i+','
                linetabl.append(i)
                

def lue_html2(sisantulotiedosto):
    """Lukee vCard-tiedoston ja palauttaa listan yhteystietosanakirjoja sekä ryhmät."""
    yhteystiedot = []
    ryhmat = {}
    nykyinen_kortti = None
    nykyinen_ryhma = None
    nykyinen_indeksi = 0

    if not os.path.exists(sisantulotiedosto):
        print(f"Virhe: Tiedostoa '{sisantulotiedosto}' ei löytynyt.")
        return

    raakarivit = []
    with open(sisantulotiedosto, 'r', encoding='utf-8') as f:
        for rivi in f: 
            if (rivi.startswith(" ") or rivi.startswith("\t")) and raakarivit:
                raakarivit[-1] = raakarivit[-1] + rivi.strip()
            else:
                rivi_strip = rivi.strip()
                if rivi_strip:
                    raakarivit.append(rivi_strip)
    j = ''
    #for i in raakarivit:
    # Käsitellään yhdistetyt rivit
    for rivi in raakarivit:
        if nykyinen_kortti:
            if '<tr>' in rivi :
                yhteystiedot.append(nykyinen_kortti)
                nykyinen_kortti = None
            
        elif '<td>' in rivi :
            print('tietue')

                        
    return yhteystiedot, ryhmat
                    
    
def lue_vcf(sisantulotiedosto):
    yhteystiedot = []
    ryhmat = []
    ryhmat2 = []
    nykyinen_kortti = None
    nykyinen_ryhma = None
    kategoriat=''
    strtmp=[]
    
    if not os.path.exists(sisantulotiedosto):
        print(f"Virhe: Tiedostoa '{sisantulotiedosto}' ei löytynyt.")
        return

    raakarivit = []
    with open(sisantulotiedosto, 'r', encoding='utf-8') as f:
        for rivi in f:
            if (rivi.startswith(" ") or rivi.startswith("\t")) and raakarivit:
                raakarivit[-1] = raakarivit[-1] + rivi.strip()
            else:
                rivi_strip = rivi.strip()
                if rivi_strip:
                    raakarivit.append(rivi_strip)
    for rivi in raakarivit:

        avain1vcf=''
        avain2vcf=''
        avain3vcf=''
        arvo=''
        arvo2=''
        emailloc=0
        
        if ':' in rivi:
            
            avain1vcf, arvo = rivi.split(":", 1)
        
            if ';' in avain1vcf:
                avain1vcf, avain2vcf = avain1vcf.split(";", 1)
                arvo2=arvo
                if ";" in avain2vcf:
                    avain2vcf, avain3vcf = avain2vcf.split(";", 1)
                                                            
            if avain1vcf == "BEGIN" and arvo == "VCARD":
                
                nykyinen_kortti = {"N": "", "FN": "", "ORG": "", "ADR": "", "TEL": [], "EMAIL": [], "CATEGORIES": [], "URL": []}
               
            elif  avain1vcf == "BEGIN" and arvo == "GROUP":
                pass
                
            elif avain1vcf == "BEGIN" and arvo == 'GRP':
                nykyinen_ryhma = {"GN": "", "GNUM": "", "MEMNUM": "", "MEMBER": []}
            elif avain1vcf == "N":
                nykyinen_kortti["N"] = arvo
     
            elif avain1vcf == "END" and arvo == "VCARD":
                if nykyinen_kortti:
                        yhteystiedot.append(nykyinen_kortti)
 
            elif avain1vcf == "END" and arvo=="GRP":
                        ryhmat2.append(nykyinen_ryhma)
            elif avain1vcf == "END" and arvo == "GROUP":
                pass
            elif avain1vcf == "FN":
                nykyinen_kortti["FN"] = arvo
            elif avain1vcf == "ORG":
                nykyinen_kortti["ORG"] = arvo
            elif avain1vcf == "ADR":
                nykyinen_kortti['ADR']=lisaa_arvo(arvo,nykyinen_kortti,'ADR',strtmp,avain2vcf,avain3vcf)
            elif avain1vcf == "TEL":
                nykyinen_kortti['TEL']=lisaa_arvo(arvo,nykyinen_kortti,'TEL',strtmp,avain2vcf,avain3vcf)
    
            elif avain1vcf == "EMAIL":
                nykyinen_kortti['EMAIL']=lisaa_arvo(arvo,nykyinen_kortti,'EMAIL',strtmp,avain2vcf,avain3vcf)

            elif avain1vcf == "TEL":
                nykyinen_kortti['URL']=lisaa_arvo(arvo,nykyinen_kortti,'URL',strtmp,avain2vcf,avain3vcf)
      
            elif avain1vcf == "CATEGORIES":
                nykyinen_kortti["CATEGORIES"]=arvo.split(",")
                ryhmat = add_to_mappings(ryhmat, kategoriat)
            elif avain1vcf == "BEGIN" and avain2vcf == "GNUM":
                nykyinen_ryhma["GNUM"] = arvo
            elif avain1vcf == "GN:":
                nykyinen_ryhma["GN"] = arvo
            elif avain1vcf == "MEMNUM":
                nykyinen_ryhma["MEMNUM"] = arvo

            elif avain1vcf == "MEMBER":
       
                nykyinen_ryhma["MEMBER"] = arvo.split(";")
            else :
                strtmp = []
                emailloc=0

    return yhteystiedot, ryhmat, ryhmat2

def lisaa_arvo(arvo,nykyinen_kortti,atr,strtmp,avain2vcf,avain3vcf):
    
    if 'PREF=1' == avain2vcf : 
        
        nykyinen_kortti['DEF'] = 1
        if ';' in avain2vcf:
            strtmp.append(etsi_loc(arvo,avain2vcf,nykyinen_kortti,atr)) 
            nykyinen_kortti[atr]=strtmp
        else :
            strtmp.append(etsi_loc(arvo,avain3vcf,nykyinen_kortti,atr))
            nykyinen_kortti[atr]=strtmp

    else :
        nykyinen_kortti['DEF'] = 0 
        strtmp.append(etsi_loc(arvo,avain2vcf,nykyinen_kortti,atr))
        nykyinen_kortti[atr]=strtmp
    
    return strtmp

def etsi_loc(arvo,avain,kortti,atr):
    j = 0
    k = avain[5:]
    
    for i in list_location:
        j += 1
        if i == k :
            rj = str(j) + ' - ' + i + ' - ' + arvo
            return rj
        
    
def add_to_mappings(ryhmat, key):
    """Lisää arvon sanakirjan listaan, jos sitä ei vielä ole."""
    if key not in ryhmat:
        ryhmat.append(key)
    return ryhmat


def printvc(kontaktit):
    """Tulostetaan lopputulos siististi näytölle.
    print(f"\n--- Löydetty yhteensä {len(kontaktit)} kontaktia ---\n")
    for k in kontaktit:
        nimi = k['FN'] if k['FN'] else k['N']
        print(f"Nimi: {nimi}")
        if k['TEL']:
            print(f"  Puhelimet: {k['TEL']}")
        if k['EMAIL']:
            print(f"  Sähköpostit: {k['EMAIL']}")
        if k['CATEGORIES']:
            print(f"  Ryhmät: {k['CATEGORIES']}")
        print("-" * 30) """

def testul(kontaktit):
    print(f"\n--- Löydetty yhteensä {len(kontaktit)} kontaktia ---\n")
    for k in kontaktit:
        l = 0
        nimi = k['FN'] if k['FN'] else k['N']
        print(f"{nimi}, ")
        if k['TEL']:
            print(f"tel {k['TEL']}, ")
        if k['EMAIL']:
            print(f"email: {k['EMAIL']}, ")
        if k['ADR']:
            print(f"address: {k['ADR']}, ")
            j = str(k['ADR'])
            j=j.replace('[\'','').replace('\']','').split(';')
            for l in range(0,7):
                
                print(f'{l},{list_address[l]},{j[l]}')
                
                
    
        if k['CATEGORIES']:
            print(f"categ {k['CATEGORIES']} ,")
        print("-" * 30)


#*********************HTML 2 *******************


def tallenna_for1_html(tulostiedosto, yhteystiedot, ryhmat):
    """Tallentaa yhteystiedot ryhmiteltynä HTML-taulukkoon."""
    with open(tulostiedosto, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Yhteystiedot ryhmittäin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        h2 { color: #333; }
    </style>
</head>
<body>
""")
        
        if ryhmat:
            for ryhma, jasenet in ryhmat.items():
                # KORJATTU: Lisätty puuttuva avaava <h2>-tägi
                f.write(f"<h2>Ryhmä: {ryhma} ({len(jasenet)} jäsentä)</h2>\n")
                f.write("<table>\n")
                f.write("    <tr><th>Nimi</th><th>Puhelin</th><th>Sähköposti</th></tr>\n")
                            
                for j_idx in jasenet:
                    if j_idx < len(yhteystiedot):
                        kortti = yhteystiedot[j_idx]
                        puh = ", ".join(kortti["TEL"]) if kortti["TEL"] else "-"
                        gml = ", ".join(kortti["EMAIL"]) if kortti["EMAIL"] else "-"
                        nimi = kortti["FN"] if kortti["FN"] else kortti["N"]
                        
                        f.write('    <tr>\n')
                        f.write(f'        <td>{nimi}</td>\n')
                        f.write(f'        <td>{puh}</td>\n')
                        f.write(f'        <td>{gml}</td>\n')
                        f.write('    </tr>\n')
                f.write('</table>\n')
        else:
            f.write("<h2>Kaikki yhteystiedot (Ei ryhmiä)</h2>\n")
            f.write("<table>\n")
            f.write("    <tr><th>Nimi</th><th>Puhelin</th><th>Sähköposti</th></tr>\n")
            for kortti in yhteystiedot:
                puh = ", ".join(kortti["TEL"]) if kortti["TEL"] else "-"
                gml = ", ".join(kortti["EMAIL"]) if kortti["EMAIL"] else "-"
                nimi = kortti["FN"] if kortti["FN"] else kortti["N"]
                f.write(f'    <tr><td>{nimi}</td><td>{puh}</td><td>{gml}</td></tr>\n')
            f.write('</table>\n')
                
        f.write('</body>\n</html>')


#******************'HTML ********************


def tallenna_taulukko_html(tulostiedosto, yhteystiedot, ryhmat):
    """Tallentaa yhteystiedot ryhmiteltynä HTML-taulukkoon."""
    with open(tulostiedosto, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html>\
<html>\
<body>\
")
        
        if yhteystiedot:
            f.write("<table>\n")
            #for i, jas in enumerate(ryhmat):
 
            #for j_idx, kortti in enumerate(yhteystiedot):
            for i, kortti in enumerate(yhteystiedot):
                #jas=ryhmat[i]
                #kortti=ryhmat[i]
                                                
                #for j_idx in kortti:
                #if j_idx < len(yhteystiedot):
                kortti = yhteystiedot[i]
                          
                f.write('<tr>\n')
                f.write(f'<td>{kortti['FN']}</td>\n')
                f.write(f'<td>{kortti['N']}</td>\n')
                f.write(f'<td>{kortti['TEL']}</td>\n')
                f.write(f'<td>{kortti['EMAIL']}</td>\n')
                f.write(f'<td>{kortti['CATEGORIES']}</td>\n')
            
            f.write('</table>\n')
        else:
            pass
             
        f.write('</body>\n</html>')

def tallenna_tiedot_vcf(tulostiedosto, yhteystiedot, ryhmat, ryhmat2):
 
    with open(tulostiedosto, 'w', encoding='utf-8') as f:
       
        # Kirjoitetaan ryhmätiedot
        if True:
            f.write("BEGIN:GROUP\n")
            f.write(f"GNUM:{len(ryhmat2)}\n")
            for i, jas in enumerate(ryhmat2):
                jas=ryhmat2[i]
                val = jas.get('MEMBER')
                                
                f.write("BEGIN:GRP\n")
                f.write(f"GN:{jas['GN']}\n")
                f.write(f"MEMNUM:{jas['MEMNUM']}\n")
                
                delimiter = " " # Define a delimiter
                join_str = delimiter.join(jas['MEMBER'])
                join_str = join_str.replace(' ',';')

                f.write(f"MEMBER:{join_str}\n")
                f.write("END:GRP\n")
                f.write("END:GROUP\n")

            
        # Kirjoitetaan osoitetiedot
        f.write("BEGIN:ADDRESS\n")
        f.write(f"ANUM {len(yhteystiedot)}\n")
        for i, kortti in enumerate(yhteystiedot):
            f.write("BEGIN:VCARD\n")
            f.write(f"N:{kortti['N']}\n")
            f.write("SEND:1\n")
            f.write("END:VCARD\n")
        f.write("END:ADDRESS\n")



# PÄÄOHJELMA
if __name__ == "__main__":

    '''
    def lue_html():
    def lue_html2(sisantulotiedosto):
    def lue_vcf(sisantulotiedosto):
    
    def printvc(kontaktit):
    def testul(kontaktit):
    
    def tallenna_for1_html(tulostiedosto, yhteystiedot, ryhmat):
    def tallenna_taulukko_html
    def tallenna_tiedot_vcf
    '''

    if len(sys.argv) <= 1 :
        input_tiedosto = input('lukutiedosto: ')
    else:
        input_tiedosto = sys.argv[1]
    if len(sys.argv) <= 2 :
        output_tiedosto = input('kirjoitustiedosto: ')
    else:
        output_tiedosto = sys.argv[2]
    
    #input_tiedosto = "y:/dev/e1.vcf"
    #output_tiedosto = "y:/dev/te.html"
    
    if not os.path.exists(input_tiedosto):
        print(f'{input_tiedosto} ei löydy.')
    else:

        print(f"Luetaan tiedostoa: {input_tiedosto}...")
        yhteystiedot, ryhmat, ryhmat2= lue_vcf(input_tiedosto)
        if yhteystiedot:
            testul(yhteystiedot)
                  
            
            tallenna_taulukko_html(output_tiedosto, yhteystiedot, ryhmat)
            print(f"Tiedot tallennettu onnistuneesti tiedostoon: {output_tiedosto}")
        else:
            print("Yhteystietoja ei voitu lukea tai tiedosto oli tyhjä.")
