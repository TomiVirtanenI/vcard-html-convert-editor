import os
import pandas as pd
import re
import numbers

loc=['home','work','other']

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
                
                #print(i,end=',')
     
    
def lue_vcf(sisantulotiedosto):
    yhteystiedot = []
    ryhmat = []
    ryhmat2 = []
    nykyinen_kortti = None
    nykyinen_ryhma = None
    kategoriat=''
    #nykyinen_kortti = {"N": "", "FN": "", "ORG": "", "ADR": "", "TEL": [], "EMAIL": [], "CATEGORIES": []}        
    print(loc)
    if not os.path.exists(sisantulotiedosto):
        print(f"Virhe: Tiedostoa '{sisantulotiedosto}' ei löytynyt.")
        return

    # Luetaan rivit ja liitetään jatkorivit (unfolding)
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

        perus_avain=''
        perus_avain2=''
        arvo=''
        arvo2=''


        #*********************itse alku *****************
        if ':' in rivi:
            
            perus_avain, arvo = rivi.split(":", 1)
        
            if ';' in perus_avain:
                perus_avain, perus_avain2 = perus_avain.split(";", 1)
                arvo2=arvo
            perus_avain2=perus_avain2.replace('PREF=1:','').replace('PREF=1;','').replace('TYPE=','')
                                                        
            if perus_avain == "BEGIN" and arvo == "VCARD":
                
                nykyinen_kortti = {"N": "", "FN": "", "ORG": "", "ADR": "", "TEL": [], "EMAIL": [], "CATEGORIES": [], "LOC": ""}
               
            elif  perus_avain == "BEGIN" and arvo == "GROUP":
                pass
                
            elif perus_avain == "BEGIN" and arvo == 'GRP':
                nykyinen_ryhma = {"GN": "", "GNUM": "", "MEMNUM": "", "MEMBER": []}
            elif perus_avain == "N":
                nykyinen_kortti["N"] = arvo
     
            elif perus_avain == "END" and arvo == "VCARD":
                if nykyinen_kortti:
                        yhteystiedot.append(nykyinen_kortti)
 
            elif perus_avain == "END" and arvo=="GRP":
                        ryhmat2.append(nykyinen_ryhma)
            elif perus_avain == "END" and arvo == "GROUP":
                pass
            elif perus_avain == "FN":
                nykyinen_kortti["FN"] = arvo
            elif perus_avain == "ORG":
                nykyinen_kortti["ORG"] = arvo
            elif perus_avain == "ADR":
                nykyinen_kortti["ADR"] = arvo
            elif perus_avain == "TEL":
                nykyinen_kortti["TEL"]=arvo.split(",")
            elif perus_avain == "EMAIL":

                nykyinen_kortti['LOC']=etsi_loc(perus_avain2,nykyinen_kortti)  

                nykyinen_kortti["EMAIL"] = arvo.split(",")
                
            elif perus_avain == "CATEGORIES":
                nykyinen_kortti["CATEGORIES"]=arvo.split(",")
                ryhmat = add_to_mappings(ryhmat, kategoriat)
            elif perus_avain == "BEGIN" and perus_avain2 == "GNUM":
                nykyinen_ryhma["GNUM"] = arvo
            elif perus_avain == "GN:":
                nykyinen_ryhma["GN"] = arvo
            elif perus_avain == "MEMNUM":
                nykyinen_ryhma["MEMNUM"] = arvo

            elif perus_avain == "MEMBER":
                #rivi = rivi[7:]
                #jasenet = [jasen.strip() for jasen in rivi.strip().split(";")]
                nykyinen_ryhma["MEMBER"] = arvo.split(";")
            
    return yhteystiedot, ryhmat, ryhmat2

def etsi_loc(avain,kortti):
    j = 1
                
    for i in loc:
        if i == avain :
            kortti['LOC']=j  
            print('löyty',j)
            return j
        j += 1
    
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
    """Tulostetaan lopputulos siististi näytölle."""
    print(f"\n--- Löydetty yhteensä {len(kontaktit)} kontaktia ---\n")
    for k in kontaktit:
        nimi = k['FN'] if k['FN'] else k['N']
        print(f"{nimi}, ")
        if k['TEL']:
            print(f"{k['TEL']}, ")
        if k['EMAIL']:
            em=k['EMAIL']
            print(f"{k['EMAIL']}, ")
        if k['CATEGORIES']:
            print(f"{k['CATEGORIES']} ,")
        if k['LOC']:
            print(f"{k['LOC']} ,")
        print("-" * 30)


#*********************HTML 2 *******************


def tallenna_tiedot_html2(tulostiedosto, yhteystiedot, ryhmat):
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


def tallenna_tiedot_html(tulostiedosto, yhteystiedot, ryhmat):
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



# PÄÄOHJELMA
if __name__ == "__main__":
    
    input_tiedosto = "y:/dev/te lista.vcf"
    output_tiedosto = "y:/dev/te.html"
    
    if not os.path.exists(input_tiedosto):
        print(f"Testitiedostoa {input_tiedosto} ei löydy. Asetetaan oletukseksi 'contacts.vcf'")
        #input_tiedosto = "contacts.vcf"
        #output_tiedosto = "demotabld5.html"
    
    # Luodaan tyhjä testitiedosto, jos sitä ei ole ollenkaan olemassa testiajoa varten
    #if not os.path.exists(input_tiedosto):
    #    with open(input_tiedosto, "w", encoding="utf-8") as f:
    #        f.write("BEGIN:VCARD\nFN:Matti Meikäläinen\nTEL:0401234567\nCATEGORIES:Kaverit,Työ\nEND:VCARD\n")

    print(f"Luetaan tiedostoa: {input_tiedosto}...")
    yhteystiedot, ryhmat, ryhmat2= lue_vcf(input_tiedosto)
    if yhteystiedot:
        #lue_html()
        #tallenna_tiedot_vcf(output_tiedosto, yhteystiedot, ryhmat, ryhmat2)
    
        #printvc(yhteystiedot)
        testul(yhteystiedot)
        #print(f"Löydetty {len(yhteystiedot)} yhteystietoa ja {len(ryhmat)} ryhmää. ")
                
        
        for kortti in yhteystiedot:
            for i_idx in kortti['EMAIL']:
                print(f'{i_idx}')
            print(f"N:{kortti['FN']} {kortti['EMAIL']} {kortti['CATEGORIES']}")
        tallenna_tiedot_html(output_tiedosto, yhteystiedot, ryhmat)
        print(f"\Tiedot tallennettu onnistuneesti tiedostoon: {output_tiedosto}")
    else:
        print("Yhteystietoja ei voitu lukea tai tiedosto oli tyhjä.")
