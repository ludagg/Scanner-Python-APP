import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image, ImageTk, ImageOps
import pyinsane2

class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖨️ Mon Scanner Pro")
        
        # Initialiser le scanner
        try:
            pyinsane2.init()
            self.scanner_initialized = True
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'initialiser le scanner: {str(e)}")
            self.scanner_initialized = False
            self.root.destroy()
            return

        self.scanned_image = None
        
        # Interface
        self.create_widgets()
        
        # Gérer la fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Frame principale
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Boutons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.btn_scan = tk.Button(
            btn_frame, 
            text="📄 Scanner un document", 
            font=("Arial", 14), 
            command=self.scanner_document,
            width=20
        )
        self.btn_scan.pack(pady=10)
        
        save_frame = tk.Frame(main_frame)
        save_frame.pack(pady=10)
        
        self.btn_png = tk.Button(
            save_frame, 
            text="💾 Enregistrer en PNG", 
            command=self.enregistrer_en_png,
            state=tk.DISABLED,
            width=15
        )
        self.btn_png.pack(side=tk.LEFT, padx=5)
        
        self.btn_pdf = tk.Button(
            save_frame, 
            text="📁 Enregistrer en PDF", 
            command=self.enregistrer_en_pdf,
            state=tk.DISABLED,
            width=15
        )
        self.btn_pdf.pack(side=tk.LEFT, padx=5)
        
        # Zone d'image
        self.label_image = tk.Label(main_frame, bg='white', bd=2, relief=tk.SUNKEN)
        self.label_image.pack(pady=10, expand=True, fill=tk.BOTH)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X)

    def choisir_scanner(self):
        try:
            devices = pyinsane2.get_devices()
            if not devices:
                messagebox.showerror("Erreur", "Aucun scanner détecté.")
                return None
            if len(devices) == 1:
                return devices[0]
            
            # Si plusieurs scanners
            noms = [d.name for d in devices]
            choice = simpledialog.askstring(
                "Choix du scanner", 
                f"Scanners disponibles:\n{', '.join(noms)}\nEntrez le nom exact :"
            )
            if choice is None:  # Annulé
                return None
                
            for d in devices:
                if d.name == choice:
                    return d
            return devices[0]  # Retourne le premier par défaut
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sélection du scanner: {str(e)}")
            return None

    def scanner_document(self):
        try:
            self.status_var.set("Recherche du scanner...")
            self.root.update()
            
            scanner = self.choisir_scanner()
            if not scanner:
                self.status_var.set("Prêt")
                return
                
            self.status_var.set("Scan en cours...")
            self.root.update()
            
            # Configurer les options de scan (peut être adapté)
            try:
                pyinsane2.set_scanner_opt(scanner, 'resolution', [300])
                pyinsane2.set_scanner_opt(scanner, 'mode', ['Color'])
            except:
                pass  # Ignorer si ces options ne sont pas disponibles
            
            scan_session = scanner.scan(multiple=False)

            while True:
                try:
                    scan_session.scan.read()
                except EOFError:
                    break

            image = scan_session.images[-1]
            self.scanned_image = image
            self.afficher_image(image)
            
            # Activer les boutons d'enregistrement
            self.btn_png.config(state=tk.NORMAL)
            self.btn_pdf.config(state=tk.NORMAL)
            
            self.status_var.set("Scan terminé")
            messagebox.showinfo("Succès", "Scan terminé !")

        except Exception as e:
            self.status_var.set("Erreur lors du scan")
            messagebox.showerror("Erreur", f"Erreur lors du scan: {str(e)}")
        finally:
            self.status_var.set("Prêt")

    def afficher_image(self, image):
        try:
            temp_path = "last_scan.png"
            image.save(temp_path)
            
            img = Image.open(temp_path)
            img = ImageOps.exif_transpose(img)  # Corriger l'orientation
            
            # Redimensionner pour l'affichage
            max_size = (600, 600)
            img.thumbnail(max_size, Image.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(img)
            self.label_image.config(image=img_tk)
            self.label_image.image = img_tk
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher l'image: {str(e)}")

    def enregistrer_en_png(self):
        if not self.scanned_image:
            messagebox.showwarning("Aucun scan", "Vous devez d'abord scanner un document.")
            return
            
        chemin = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Image PNG", "*.png"), ("Tous les fichiers", "*.*")],
            title="Enregistrer l'image"
        )
        
        if chemin:
            try:
                self.scanned_image.save(chemin)
                messagebox.showinfo("Sauvé", f"Image enregistrée sous:\n{chemin}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")

    def enregistrer_en_pdf(self):
        if not self.scanned_image:
            messagebox.showwarning("Aucun scan", "Vous devez d'abord scanner un document.")
            return
            
        chemin = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
            title="Enregistrer le PDF"
        )
        
        if chemin:
            try:
                self.scanned_image.save(chemin, "PDF", resolution=100.0)
                messagebox.showinfo("Sauvé", f"PDF enregistré sous:\n{chemin}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")

    def on_close(self):
        if self.scanner_initialized:
            pyinsane2.exit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerApp(root)
    root.mainloop()
