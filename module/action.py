# module/action.py
import time
import asyncio
from module import modul, envwebchat, envstatus, envfile, envreport, envfolder, envtelegram, envinstagram, envhitllm
from module.modul import log_function_status


@log_function_status
def actions_webchat(driver, json_data, report_filename, id_test, time_start, today, tester_name, url, title_page, browser_name):
    start = modul.start_time()
    class_name = "message-content-wrapper"
    content = "content"
    title = "当 Membaca pertanyaan dan mengirim ke webchat"
    modul.show_loading(title)
    print("\n")
    count_per_element_title = len(json_data)
    question_count = sum(sum(1 for key in item if key.startswith("pertanyaan")) for item in json_data)
    for element in json_data:
        modul.refresh(driver)
        modul.wait_time(3)
        duration_pertitle = modul.start_time()
        modul.show_loading(element.get("title", "Untitled"))
        print("\n")
        count = 0
        for key, value in element.items():
            if key.startswith("pertanyaan") and value is not None and str(value).strip() != "":
                count += 1
                duration_perquestion = modul.start_time()
                question = str(value) # Ensure question is a string
                envwebchat.send_message(driver, question)
                envwebchat.wait_reply(driver, class_name, content, question)
                if count % 5 == 0:
                    modul.wait_time(2)
                    modul.refresh(driver)
                image_capture = envreport.take_screenshot(driver, id_test, key, question)
                respond_bot = envwebchat.get_reply_chat(driver, class_name, content, question)
                respond_bot = "\n".join(respond_bot).strip()
                respond_bot = envstatus.respond_bot_correction(respond_bot)
                title_loading = f"{key} : {question}"
                modul.show_loading_sampletext(title_loading)
                respond_csv = str(element.get("context", "")).strip()
                respond_csv = envstatus.respond_csv_correction(respond_csv)
                end_duration_persampletext = modul.end_time(duration_perquestion)
                
                # Mengaktifkan evaluasi LLM
                skor, _, explanation, AI = envhitllm.hit_llm_to_scoring_gemini(respond_bot, respond_csv)
                
                status = envstatus.status(skor)
                data_bot = {
                    "no": element.get("no", ""),
                    "title": element.get("title", ""),
                    "question": question,
                    "response_kb": respond_csv,
                    "response_llm": respond_bot,
                    "status": status,
                    "duration": end_duration_persampletext,
                    "image_capture": image_capture,
                    "skor": skor,
                    "explanation": explanation
                }
                envfile.write_json_data_bot(data_bot, report_filename, id_test)
                pass_count, failed_count = envstatus.calculate(report_filename, id_test)
                data_summary = {
                    "id_test": id_test,
                    "tester_name": tester_name,
                    "ai_evaluation": AI,
                    "url": url,
                    "page_name": title_page,
                    "browser_name": browser_name,
                    "date_test": today,
                    "start_time_test": time_start,
                    "total_title": count_per_element_title,
                    "total_question": question_count,
                    "success": pass_count,
                    "failed": failed_count
                }
                envfile.write_json_data_summary(data_summary, report_filename, id_test)
                envreport.report_action(report_filename, id_test)
        end_duration_pertitle = modul.end_time(duration_pertitle)
        chart = {element.get("title", "Untitled"): end_duration_pertitle}
        envfile.write_json_chart(chart, report_filename, id_test)
        print(f"\n竢ｳ Total durasi Topik '{element.get('title', 'Untitled')}' : {end_duration_pertitle}\n")
    print("識 Topik Terakhir \n")

@log_function_status
async def actions_telegram(target_bot_username, greeting, json_data, report_filename, id_test, time_start, today, tester_name):
    modul.show_loading(f"Mengirim sapaan awal ke {target_bot_username}...")
    await envtelegram.send_message_to_bot(target_bot_username, greeting)
    await asyncio.sleep(5)
    print("\n")
    title = f"当 Membaca pertanyaan dan mengirim ke {target_bot_username}"
    modul.show_loading(title)
    print("\n")
    count_per_element_title = len(json_data)
    question_count = sum(sum(1 for key in item if key.startswith("pertanyaan")) for item in json_data)
    for element in json_data:
        duration_pertitle = modul.start_time()
        modul.show_loading(element.get("title", "Untitled"))
        print("\n")
        for key, value in element.items():
            if key.startswith("pertanyaan") and value is not None and str(value).strip() != "":
                duration_perquestion = modul.start_time()
                question = str(value) # Ensure question is a string
                await envtelegram.send_message_to_bot(target_bot_username, question)
                await asyncio.sleep(15)
                respond_bot = await envtelegram.get_latest_message_from_bot(target_bot_username)
                if not respond_bot:
                    respond_bot = "Error: Tidak ada balasan dari bot setelah menunggu."
                title_loading = f"{key} : {question}"
                modul.show_loading_sampletext(title_loading)
                respond_csv = str(element.get("context", "")).strip()
                respond_csv = envstatus.respond_csv_correction(respond_csv)
                end_duration_persampletext = modul.end_time(duration_perquestion)
                
                # Mengaktifkan evaluasi LLM
                skor, _, explanation, AI = envhitllm.hit_llm_to_scoring_gemini(respond_bot, respond_csv)
                
                status = envstatus.status(skor)
                image_capture = None
                data_bot = {
                    "no": element.get("no", ""),
                    "title": element.get("title", ""),
                    "question": question,
                    "response_kb": respond_csv,
                    "response_llm": respond_bot,
                    "status": status,
                    "duration": end_duration_persampletext,
                    "image_capture": image_capture,
                    "skor": skor,
                    "explanation": explanation
                }
                envfile.write_json_data_bot(data_bot, report_filename, id_test)
                pass_count, failed_count = envstatus.calculate(report_filename, id_test)
                data_summary = {
                    "id_test": id_test,
                    "tester_name": tester_name,
                    "ai_evaluation": AI,
                    "url": f"Telegram Bot ({target_bot_username})",
                    "page_name": "Telegram Test",
                    "browser_name": "Telethon",
                    "date_test": today,
                    "start_time_test": time_start,
                    "total_title": count_per_element_title,
                    "total_question": question_count,
                    "success": pass_count,
                    "failed": failed_count
                }
                envfile.write_json_data_summary(data_summary, report_filename, id_test)
                envreport.report_action(report_filename, id_test)
        end_duration_pertitle = modul.end_time(duration_pertitle)
        chart = {element.get("title", "Untitled"): end_duration_pertitle}
        envfile.write_json_chart(chart, report_filename, id_test)
        print(f"\n竢ｳ Total durasi Topik '{element.get('title', 'Untitled')}' : {end_duration_pertitle}\n")
    print("識 Topik Terakhir \n")
    # modul.close_browser(driver)

@log_function_status
async def actions_facebook(target_username, greeting, json_data, report_filename, id_test, time_start, today, tester_name):
    try:
        modul.show_loading(f"Initializing Facebook API and session...")
        fb_client = envfacebook.FacebookClient()

        if not fb_client.access_token:
            error_msg = "Facebook access token failed to load. Check environment variables and token file."
            print(error_msg)
            envstatus.log_error(f"Facebook Error: {error_msg}", tester_name, id_test)
            return
        envstatus.log_status("Facebook client initialized successfully.", tester_name, id_test, status="success")
    except Exception as e:
        error_msg = f"Failed to initialize Facebook client: {str(e)}"
        print(error_msg)
        envstatus.log_error(f"Facebook Initialization Error: {error_msg}", tester_name, id_test)
        return

    modul.show_loading(f"Mengirim sapaan awal ke {target_username}...")
    fb_client.send_message(target_username, greeting)
    await asyncio.sleep(5) # Give time for the greeting to be processed
    print("\n")

    title = f"当 Membaca pertanyaan dan mengirim ke {target_username}"
    modul.show_loading(title)
    print("\n")

    count_per_element_title = len(json_data)
    question_count = sum(sum(1 for key in item if key.startswith("pertanyaan")) for item in json_data)

    for element in json_data:
        duration_pertitle = modul.start_time()
        modul.show_loading(element.get("title", "Untitled"))
        print("\n")

        for key, value in element.items():
            if key.startswith("pertanyaan") and value is not None and str(value).strip() != "":
                duration_perquestion = modul.start_time()
                question = str(value)

                try:
                    fb_client.send_message(target_username, question)
                    await asyncio.sleep(15) # Wait for response
                    
                    respond_bot_obj = fb_client.get_latest_message()
                    respond_bot = respond_bot_obj["message_text"] if respond_bot_obj else "Error: No response from bot after waiting."
                    
                    # Log successful message delivery
                    envstatus.log_status(
                        f"Message sent to {target_username}",
                        tester_name,
                        id_test,
                        status="success",
                        additional_info={"question": question, "response": respond_bot}
                    )
                except Exception as e:
                    error_msg = f"Failed to send/receive message: {str(e)}"
                    print(error_msg)
                    envstatus.log_error(
                        f"Facebook Message Error: {error_msg}",
                        tester_name,
                        id_test,
                        additional_info={"question": question}
                    )
                    respond_bot = error_msg

                title_loading = f"{key} : {question}"
                modul.show_loading_sampletext(title_loading)
                respond_csv = str(element.get("context", "")).strip()
                respond_csv = envstatus.respond_csv_correction(respond_csv)
                end_duration_persampletext = modul.end_time(duration_perquestion)
                
                # Mengaktifkan evaluasi LLM
                skor, _, explanation, AI = envllmscore.llm_score(respond_bot, respond_csv)
                
                status = envstatus.status(skor)
                image_capture = None # No screenshot for Facebook Messenger via Graph API
                data_bot = {
                    "no": element.get("no", ""),
                    "title": element.get("title", ""),
                    "question": question,
                    "response_kb": respond_csv,
                    "response_llm": respond_bot,
                    "status": status,
                    "duration": end_duration_persampletext,
                    "image_capture": image_capture,
                    "skor": skor,
                    "explanation": explanation
                }
                envfile.write_json_data_bot(data_bot, report_filename, id_test)
                pass_count, failed_count = envstatus.calculate(report_filename, id_test)
                data_summary = {
                    "id_test": id_test,
                    "tester_name": tester_name,
                    "ai_evaluation": AI,
                    "url": f"Facebook Messenger ({target_username})",
                    "page_name": "Facebook Test",
                    "browser_name": "Graph API",
                    "date_test": today,
                    "start_time_test": time_start,
                    "total_title": count_per_element_title,
                    "total_question": question_count,
                    "success": pass_count,
                    "failed": failed_count
                }
                envfile.write_json_data_summary(data_summary, report_filename, id_test)
                envreport.report_action(report_filename, id_test)
        end_duration_pertitle = modul.end_time(duration_pertitle)
        chart = {element.get("title", "Untitled"): end_duration_pertitle}
        envfile.write_json_chart(chart, report_filename, id_test)
        print(f"\n竢ｳ Total durasi Topik '{element.get('title', 'Untitled')}' : {end_duration_pertitle}\n")
    print("識 Topik Terakhir \n")
    # No logout needed for Graph API


@log_function_status
async def actions_instagram(target_username, greeting, json_data, report_filename, id_test, time_start, today, tester_name):
    modul.show_loading(f"Initializing Instagram API and session...")
    envinstagram.initialize_instagram_api()

    modul.show_loading(f"Mengirim sapaan awal ke {target_username}...")
    # Kirim sapaan dan dapatkan timestamp setelah pesan terkirim
    greeting_timestamp = envinstagram.send_message(target_username, greeting)
    if greeting_timestamp:
        # Tunggu sebentar untuk memastikan bot sempat merespons sapaan (jika ada)
        await asyncio.sleep(10)
    print("\n")

    title = f"当 Membaca pertanyaan dan mengirim ke {target_username}"
    modul.show_loading(title)
    print("\n")

    count_per_element_title = len(json_data)
    question_count = sum(sum(1 for key in item if key.startswith("pertanyaan")) for item in json_data)

    for element in json_data:
        duration_pertitle = modul.start_time()
        modul.show_loading(element.get("title", "Untitled"))
        print("\n")

        for key, value in element.items():
            if key.startswith("pertanyaan") and value is not None and str(value).strip() != "":
                duration_perquestion = modul.start_time()
                question = str(value)

                # Kirim pertanyaan dan dapatkan timestamp setelah pesan terkirim
                sent_timestamp = envinstagram.send_message(target_username, question)
                
                respond_bot = ""
                if sent_timestamp:
                    # Cari pesan balasan yang datang SETELAH timestamp pesan kita
                    respond_bot = envinstagram.get_latest_message(target_username, sent_timestamp)
                
                if not respond_bot:
                    respond_bot = "Error: Tidak ada balasan dari bot setelah menunggu."

                title_loading = f"{key} : {question}"
                modul.show_loading_sampletext(title_loading)

                respond_csv = str(element.get("context", "")).strip()
                respond_csv = envstatus.respond_csv_correction(respond_csv)
                end_duration_persampletext = modul.end_time(duration_perquestion)

                # Activate LLM evaluation
                skor, _, explanation, AI = envllmscore.llm_score(respond_bot, respond_csv)

                status = envstatus.status(skor)
                image_capture = None

                data_bot = {
                    "no": element.get("no", ""),
                    "title": element.get("title", ""),
                    "question": question,
                    "response_kb": respond_csv,
                    "response_llm": respond_bot,
                    "status": status,
                    "duration": end_duration_persampletext,
                    "image_capture": image_capture,
                    "skor": skor,
                    "explanation": explanation
                }
                envfile.write_json_data_bot(data_bot, report_filename, id_test)

                pass_count, failed_count = envstatus.calculate(report_filename, id_test)
                data_summary = {
                    "id_test": id_test,
                    "tester_name": tester_name,
                    "ai_evaluation": AI,
                    "url": f"Instagram DM (@{target_username})",
                    "page_name": "Instagram Test",
                    "browser_name": "Instagrapi",
                    "date_test": today,
                    "start_time_test": time_start,
                    "total_title": count_per_element_title,
                    "total_question": question_count,
                    "success": pass_count,
                    "failed": failed_count
                }
                envfile.write_json_data_summary(data_summary, report_filename, id_test)
                envreport.report_action(report_filename, id_test)

        end_duration_pertitle = modul.end_time(duration_pertitle)
        chart = {element.get("title", "Untitled"): end_duration_pertitle}
        envfile.write_json_chart(chart, report_filename, id_test)
        print(f"\n竢ｳ Total durasi Topik '{element.get('title', 'Untitled')}' : {end_duration_pertitle}\n")

    print("識 Topik Terakhir \n")