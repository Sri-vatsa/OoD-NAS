import torch
import wandb

wandb.init(project="SMR-OoD-NAS", name="run_w_gen_start", entity="smr-team-5")

filepath_no_gen = "./train_out/pacs-2-2-num_classes-10/0.025_0.0003_16_20_2022-10-25 20:53:13/trlog"
filepath_w_gen_mid = "./train_out/pacs-2-2-num_classes-10/0.025_0.0003_16_20_2022-10-25 21:46:40/trlog"
filepath_w_gen_start = "./train_out/pacs-2-2-num_classes-10/0.025_0.0003_16_20_2022-10-25 22:54:13/trlog"


data = torch.load(filepath_w_gen_start)

wandb.config = data['args']

wandb.define_metric("loss", summary="min")
wandb.define_metric("acc", summary="max")

loss_list = data['train_loss']
acc_list = data['test_acc']
for epoch in range(len(loss_list)):
    wandb.log({'acc': acc_list[epoch],
                'loss': loss_list[epoch]})

wandb.finish()
#print(data)

'''
wandb.init(project="SMR-OoD-NAS", name="run_w_gen_mid" entity="smr-team-5")
data1 = torch.load(filepath_w_gen_mid)

wandb.config = data1['args']
wandb.log({'test_acc': data1['test_acc'],
            'max_acc': data1['max_acc']})

print(data1)
'''