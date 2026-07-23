import os
import shutil
from PIL import Image
from sentence_transformers import SentenceTransformer, util
import json


# ------------------ LOAD MODELS ------------------

clip_model = SentenceTransformer("clip-ViT-L-14")
text_model = SentenceTransformer("all-MiniLM-L6-v2")

extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# ------------------ IMAGE MATCHING ------------------

def compare_images(img1, folder_path):

    image1 = Image.open(img1).convert("RGB")
    embedding1 = clip_model.encode(image1, convert_to_tensor=True)

    best_similarity = -1
    best_image = None

    for filename in os.listdir(folder_path):

        if filename.lower().endswith(extensions):

            img2 = os.path.join(folder_path, filename)

            image2 = Image.open(img2).convert("RGB")
            embedding2 = clip_model.encode(image2, convert_to_tensor=True)

            similarity = util.cos_sim(embedding1, embedding2).item()

            # Keep track of best match
            if similarity > best_similarity:
                best_similarity = similarity
                best_image = img2

    # Print only after checking all images
    if best_image is not None:
        print(f"\nBest Image Match : {os.path.basename(best_image)}")
        print(f"Image Similarity : {best_similarity:.4f}")
    else:
        print("\nNo image found in the folder.")

    return best_similarity, best_image


# ------------------ TEXT MATCHING ------------------

def compare_text(info, folder_path):

    input_embedding = text_model.encode(info, convert_to_tensor=True)

    best_score = -1
    best_file = None
    best_report = None

    for filename in os.listdir(folder_path):

        if filename.endswith(".txt"):

            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            file_text = f"{data['info']['Item']} {data['info']['Description']}"

            file_embedding = text_model.encode(file_text, convert_to_tensor=True)

            score = util.cos_sim(input_embedding, file_embedding).item()

            # Keep track of best match
            if score > best_score:
                best_score = score
                best_file = filename
                best_report = data

    # Print only after checking all files
    if best_file is not None:
        print(f"\nBest Text Match : {best_file}")
        print(f"Text Similarity : {best_score:.4f}")
    else:
        print("\nNo matching text found.")

    return best_file, best_score, best_report

# ------------------ MAIN PROGRAM ------------------

while True:

    choice = input(
        "\n1. Found Report\n"
        "2. Lost Report\n"
        "3. Exit\n"
        "Enter choice: "
    )

    if choice == "3":
        print("Thank you!")
        break

    img1 = input("Enter image path: ").strip().strip('"').strip("'")

    info = {
        "Item": input("Item Type: "),
        "Description": input("Description: ")
    }

    passenger = {
        "Name": input("Your Name: "),
        "Phone": input("Phone Number: "),
        "Address": input("Your Address: "),
        "PNR": input("Enter PNR: ")
    }

    # ---------------- FOUND REPORT ----------------

    if choice == "1":

        folder_path = r"C:\python\Railway Lost and Found system\lost_images"
        data_folder = r"C:\python\Railway Lost and Found system\lost_data"


        best_similarity, best_image = compare_images(img1, folder_path)

        input_text = f"{info['Item']} {info['Description']}"
        best_file, best_score, best_report = compare_text(input_text, data_folder)
        
        final_score = (best_similarity + best_score) / 2

        if final_score >= 0.80:
        
            print("\n✅ Match Found")
            
            print(".....FOUNDER INFORMATION.....:")
            print(passenger)
            
            print("\n.....OWNER INFORMATION.....")
            print(best_report["passenger"])
               
        else:

            image_name = os.path.basename(img1)
            shutil.copy(img1,
                        os.path.join(r"C:\python\Railway Lost and Found system\found_images",
                                     image_name))

            text_name = os.path.splitext(image_name)[0] + ".txt"

            with open(os.path.join(r"C:\python\Railway Lost and Found system\found_data",
                       text_name), "w") as f:

                json.dump(
        {
            "passenger": passenger,
            "info": info
        },
        f,
        indent=4
    )

            print("\nNo Match Found \nFound Report Saved")

            break

    # ---------------- LOST REPORT ----------------

    elif choice == "2":

        folder_path = r"C:\python\Railway Lost and Found system\found_images"
        data_folder = r"C:\python\Railway Lost and Found system\found_data"

        best_similarity, best_image = compare_images(img1, folder_path)

        input_text = f"{info['Item']} {info['Description']}"
        best_file, best_score, best_report = compare_text(input_text, data_folder)

        final_score = (best_similarity + best_score) / 2
        
        if final_score >= 0.80:
                    
            print("\n✅ Match Found")
                    
            print("\n.....OWNER INFORMATION.....")
            print(passenger)
                    
            print(".....FOUNDER INFORMATION.....")
            print(best_report["passenger"])
                       
                

        else:

            image_name = os.path.basename(img1)
            shutil.copy(img1,
                        os.path.join(r"C:\python\Railway Lost and Found system\lost_images",
                                     image_name))

            text_name = os.path.splitext(image_name)[0] + ".txt"
            text_path = os.path.join(data_folder, text_name)

            with open(os.path.join(r"C:\python\Railway Lost and Found system\lost_data",
                       text_name), "w") as f:

                json.dump(
                    {
                        "passenger": passenger,
                        "info": info
                    },
                    f,
                    indent=4
                )

            print("\nNo Match Found\nLost Report Saved")

        break

    else:
        print("Invalid Choice")
        break